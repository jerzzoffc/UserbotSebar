from command import pantun_cmd
from helpers import CMD

IS_PRO = True

__MODULES__ = "Pantun"
__HELP__ = """<blockquote>Command Help **Pantun**</blockquote>
<blockquote expandable>--**Basic Commands**--

    **You can create pantun with the theme**
        `{0}pantun percintaan` 
        `{0}pantun bijak`
        `{0}pantun masa depan`
        `{0}pantun motivasi`
        `{0}pantun jenaka`
        `{0}pantun nasihat`
        `{0}pantun agama`
        `{0}pantun random`</blockquote>
        
<blockquote expandable>--**Tebakan Commands**--
    **You can create tebakan with the theme**
        `{0}tebakan percintaan` 
        `{0}tebakan bijak`
        `{0}tebakan masa depan`
        `{0}tebakan motivasi`
        `{0}tebakan jenaka`
        `{0}tebakan nasihat`
        `{0}tebakan agama`
        `{0}tebakan random`</blockquote>
        
<blockquote expandable>--**Lelucon Commands**--
    **You can create lelucon with the theme**
        `{0}lelucon percintaan` 
        `{0}lelucon bijak`
        `{0}lelucon masa depan`
        `{0}lelucon motivasi`
        `{0}lelucon jenaka`
        `{0}lelucon nasihat`
        `{0}lelucon agama`
        `{0}lelucon random`</blockquote>
        
<blockquote expandable>--**Quotes Commands**--
    **You can create quotes with the theme**
        `{0}quotes percintaan` 
        `{0}quotes bijak`
        `{0}quotes masa depan`
        `{0}quotes motivasi`
        `{0}quotes jenaka`
        `{0}quotes nasihat`
        `{0}quotes agama`
        `{0}quotes random`</blockquote>
    
<blockquote expandable>--**Puisi Commands**--
    **You can create puisi with the theme**
        `{0}puisi percintaan` 
        `{0}puisi bijak`
        `{0}puisi masa depan`
        `{0}puisi motivasi`
        `{0}puisi jenaka`
        `{0}puisi nasihat`
        `{0}puisi agama`
        `{0}puisi random`</blockquote>
<b>   {1}</b>
"""


@CMD.UBOT("pantun|tebakan|lelucon|puisi|quotes")
async def _(client, message):
    return await pantun_cmd(client, message)
