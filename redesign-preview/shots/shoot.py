import asyncio, pathlib
from playwright.async_api import async_playwright
base=pathlib.Path(__file__).resolve().parent.parent
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
        for page in ["index","partners"]:
            for name,vp,mob in [("desktop",{"width":1440,"height":900},False),("mobile",{"width":390,"height":844},True)]:
                ctx=await b.new_context(viewport=vp,device_scale_factor=2 if mob else 1,is_mobile=mob,has_touch=mob)
                pg=await ctx.new_page()
                await pg.goto(f"file://{base}/{page}.html",wait_until="networkidle")
                await pg.evaluate("document.fonts.ready")
                await pg.add_style_tag(content=".header{position:static}.preview-tag{display:none}")
                await pg.wait_for_timeout(800)
                out=base/"shots"/f"{'home' if page=='index' else page}-{name}.png"
                await pg.screenshot(path=str(out),full_page=True); print(out)
                await ctx.close()
        await b.close()
asyncio.run(main())
