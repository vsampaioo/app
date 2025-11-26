from playwright.async_api import async_playwright
import asyncio

async def buscar_produto_ml(produto_digitado):
    lista_resultados = []

    async with async_playwright() as p:
    
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"Buscando por: {produto_digitado}...")
        await page.goto(f"https://lista.mercadolivre.com.br/{produto_digitado}")
        
        try:
           
            try:
                await page.wait_for_selector(".ui-search-layout__item", timeout=3000)
                itens = await page.locator(".ui-search-layout__item").all()
                seletor_preco = ".andes-money-amount__fraction"
            except:
                await page.wait_for_selector(".poly-card", timeout=3000)
                itens = await page.locator(".poly-card").all()
                seletor_preco = ".andes-money-amount__fraction"

            print(f"Encontrei {len(itens)} itens. Processando...")

           
            for i, item in enumerate(itens[:3]):
                try:
                   
                    if await item.locator("h2").count() > 0:
                        titulo = await item.locator("h2").first.inner_text()
                    else:
                        titulo = await item.locator("a").first.inner_text()
                    
                    link = await item.locator("a").first.get_attribute("href")
                    preco_texto = await item.locator(seletor_preco).first.inner_text()
                    
                    lista_resultados.append({
                        "nome": titulo,
                        "preco_atual": preco_texto,
                        "link": link
                    })
                except Exception as e:
                    print(f"Erro no item {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro geral na busca: {e}")
            
        await browser.close()
        
    return lista_resultados