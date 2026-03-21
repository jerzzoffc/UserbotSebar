import asyncio
import threading
import time
from datetime import datetime
from typing import Callable, Dict, List, Optional

import psutil
import pytz

from logs import logger


class Monitor:
    def __init__(
        self, default_interval: int = 5, logger=None, timezone: str = "Asia/Jakarta"
    ):
        self.start_time = time.time()
        self.default_interval = default_interval
        self.monitoring_active = False
        self.monitoring_task = None
        self.monitoring_data = []
        self.callbacks = []
        self.logger = logger
        try:
            self.timezone = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            self.logger.warning(
                f"Unknown timezone: {timezone}, using Asia/Jakarta as default"
            )
            self.timezone = pytz.timezone("Asia/Jakarta")

    def get_current_datetime(self, timestamp: Optional[float] = None) -> str:
        if timestamp is None:
            timestamp = time.time()

        utc_dt = datetime.utcfromtimestamp(timestamp)
        utc_dt = pytz.UTC.localize(utc_dt)
        local_dt = utc_dt.astimezone(self.timezone)

        return local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")

    def get_current_datetime_obj(self, timestamp: Optional[float] = None) -> datetime:
        if timestamp is None:
            timestamp = time.time()

        utc_dt = datetime.utcfromtimestamp(timestamp)
        utc_dt = pytz.UTC.localize(utc_dt)
        local_dt = utc_dt.astimezone(self.timezone)

        return local_dt

    def get_system_info(self) -> Dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "CPU_TOTAL": psutil.cpu_count(),
            "CPU_USAGE": cpu_percent,
            "RAM_TOTAL": memory.total,
            "RAM_USAGE": memory.used,
            "RAM_PERCENT": memory.percent,
            "STORAGE_TOTAL": disk.total,
            "STORAGE_USAGE": disk.used,
            "STORAGE_PERCENT": (disk.used / disk.total) * 100,
            "UPTIME": time.time() - self.start_time,
        }

    def get_process_info(self, pid: Optional[int] = None) -> Dict:
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)

            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            return {
                "PID": process.pid,
                "NAME_TASK": process.name(),
                "STATUS": process.status(),
                "CPU_USAGE": cpu_percent,
                "RAM_USAGE": memory_info.rss,
                "RAM_PERCENT": memory_percent,
                "THREADS": process.num_threads(),
                "CREATE_TIME": process.create_time(),
                "CMDLINE": " ".join(process.cmdline()) if process.cmdline() else "",
                "PARENT_PID": process.ppid(),
                "USERNAME": (
                    process.username() if hasattr(process, "username") else "N/A"
                ),
            }
        except psutil.NoSuchProcess:
            return {"error": f"Process dengan PID {pid} tidak ditemukan"}
        except psutil.AccessDenied:
            return {"error": f"Akses ditolak untuk PID {pid}"}

    def get_all_processes(self) -> List[Dict]:
        processes = []

        for process in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status"]
        ):
            try:
                process_info = process.info
                memory_info = process.memory_info()

                processes.append(
                    {
                        "PID": process_info["pid"],
                        "NAME_TASK": process_info["name"],
                        "STATUS": process_info["status"],
                        "CPU_USAGE": process_info["cpu_percent"],
                        "RAM_USAGE": memory_info.rss,
                        "RAM_PERCENT": process_info["memory_percent"],
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return processes

    def get_top_processes_by_cpu(self, limit: int = 10) -> List[Dict]:
        processes = self.get_all_processes()
        return sorted(processes, key=lambda x: x["CPU_USAGE"] or 0, reverse=True)[
            :limit
        ]

    def get_top_processes_by_memory(self, limit: int = 10) -> List[Dict]:
        processes = self.get_all_processes()
        return sorted(processes, key=lambda x: x["RAM_PERCENT"] or 0, reverse=True)[
            :limit
        ]

    def get_network_info(self) -> Dict:
        net_io = psutil.net_io_counters()

        return {
            "BYTES_SENT": net_io.bytes_sent,
            "BYTES_RECV": net_io.bytes_recv,
            "PACKETS_SENT": net_io.packets_sent,
            "PACKETS_RECV": net_io.packets_recv,
            "ERRORS_IN": net_io.errin,
            "ERRORS_OUT": net_io.errout,
            "DROPS_IN": net_io.dropin,
            "DROPS_OUT": net_io.dropout,
        }

    def get_disk_info(self) -> List[Dict]:
        disks = []
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(
                    {
                        "DEVICE": partition.device,
                        "MOUNTPOINT": partition.mountpoint,
                        "FILESYSTEM": partition.fstype,
                        "STORAGE_TOTAL": usage.total,
                        "STORAGE_USAGE": usage.used,
                        "STORAGE_FREE": usage.free,
                        "STORAGE_PERCENT": (usage.used / usage.total) * 100,
                    }
                )
            except PermissionError:
                continue

        return disks

    async def start(
        self, interval: Optional[int] = None, callback: Optional[Callable] = None
    ):
        if self.monitoring_active:
            self.logger.info("Monitoring sudah aktif!")
            return

        interval = interval or self.default_interval
        self.monitoring_active = True
        self.monitoring_data = []

        if callback:
            self.callbacks.append(callback)

        async def monitoring_loop():
            while self.monitoring_active:
                try:
                    timestamp = time.time()
                    system_info = self.get_system_info()
                    top_processes = self.get_top_processes_by_cpu(5)
                    network_info = self.get_network_info()

                    monitoring_record = {
                        "timestamp": timestamp,
                        "datetime": self.get_current_datetime(timestamp),
                        "system_info": system_info,
                        "top_processes": top_processes,
                        "network_info": network_info,
                    }

                    self.monitoring_data.append(monitoring_record)

                    for callback_func in self.callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback_func):
                                await callback_func(monitoring_record)
                            else:
                                callback_func(monitoring_record)
                        except Exception as e:
                            self.logger.error(f"Error in callback: {e}")

                    if len(self.monitoring_data) > 1000:
                        self.monitoring_data.pop(0)

                    await asyncio.sleep(interval)

                except Exception as e:
                    self.logger.error(f"Error dalam monitoring: {e}")
                    await asyncio.sleep(interval)

        self.monitoring_task = asyncio.create_task(monitoring_loop())
        self.logger.info(f"Monitoring dimulai dengan interval {interval} detik")

    def start_continuous_monitoring_sync(
        self, interval: Optional[int] = None, callback: Optional[Callable] = None
    ):
        if self.monitoring_active:
            self.logger.info("Monitoring sudah aktif!")
            return

        interval = interval or self.default_interval
        self.monitoring_active = True
        self.monitoring_data = []

        if callback:
            self.callbacks.append(callback)

        def monitoring_loop():
            while self.monitoring_active:
                try:
                    timestamp = time.time()
                    system_info = self.get_system_info()
                    top_processes = self.get_top_processes_by_cpu(5)
                    network_info = self.get_network_info()

                    monitoring_record = {
                        "timestamp": timestamp,
                        "datetime": self.get_current_datetime(timestamp),
                        "system_info": system_info,
                        "top_processes": top_processes,
                        "network_info": network_info,
                    }

                    self.monitoring_data.append(monitoring_record)

                    for callback_func in self.callbacks:
                        try:
                            callback_func(monitoring_record)
                        except Exception as e:
                            self.logger.error(f"Error in callback: {e}")

                    if len(self.monitoring_data) > 1000:
                        self.monitoring_data.pop(0)

                    time.sleep(interval)

                except Exception as e:
                    self.logger.error(f"Error dalam monitoring: {e}")
                    time.sleep(interval)

        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info(f"Monitoring dimulai dengan interval {interval} detik")

    async def stop(self):
        if not self.monitoring_active:
            self.logger.info("Monitoring tidak aktif!")
            return

        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.callbacks.clear()
        self.logger.info("Monitoring dihentikan")

    def get_monitoring_data(self, last_n: Optional[int] = None) -> List[Dict]:
        if last_n:
            return self.monitoring_data[-last_n:]
        return self.monitoring_data.copy()

    def add_callback(self, callback: Callable):
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    async def monitor_specific_processes_async(
        self, pids: List[int], interval: int = 5, duration: int = 60
    ) -> List[Dict]:
        monitoring_data = []
        start_time = time.time()

        while (time.time() - start_time) < duration:
            timestamp = time.time()
            record = {
                "timestamp": timestamp,
                "datetime": self.get_current_datetime(timestamp),
                "processes": [],
            }

            for pid in pids:
                process_info = self.get_process_info(pid)
                record["processes"].append(process_info)

            monitoring_data.append(record)
            await asyncio.sleep(interval)

        return monitoring_data

    def get_system_snapshot(self) -> Dict:
        return {
            "timestamp": time.time(),
            "datetime": self.get_current_datetime(),
            "system_info": self.get_system_info(),
            "all_processes": self.get_all_processes(),
            "network_info": self.get_network_info(),
            "disk_info": self.get_disk_info(),
            "top_cpu_processes": self.get_top_processes_by_cpu(5),
            "top_memory_processes": self.get_top_processes_by_memory(5),
        }

    def export_monitoring_data(self, filename: str, format: str = "json"):
        import json

        if format.lower() == "json":
            with open(filename, "w") as f:
                json.dump(self.monitoring_data, f, indent=2)
        elif format.lower() == "csv":
            import csv

            if self.monitoring_data:
                with open(filename, "w", newline="") as f:
                    flattened_data = []
                    for record in self.monitoring_data:
                        flat_record = {
                            "timestamp": record["timestamp"],
                            "datetime": record["datetime"],
                            "cpu_usage": record["system_info"]["CPU_USAGE"],
                            "ram_percent": record["system_info"]["RAM_PERCENT"],
                            "storage_percent": record["system_info"]["STORAGE_PERCENT"],
                        }
                        flattened_data.append(flat_record)

                    writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_data)

        self.logger.info(f"Data monitoring berhasil diekspor ke {filename}")

    def format_bytes(self, bytes_value: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


monitor = Monitor(default_interval=5, logger=logger, timezone="Asia/Jakarta")
