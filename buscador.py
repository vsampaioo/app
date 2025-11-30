from playwright.async_api import async_playwright
import asyncio
import unicodedata

# --- Funções Auxiliares ---

def normalizar_texto(texto):
    # Remove acentos e deixa minusculo (Ex: "Fogão" -> "fogao")
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()

def converter_preco_float(texto):
    try:
        limpo = "".join([c for c in texto if c.isdigit() or c == ','])
        limpo = limpo.replace(",", ".")
        return float(limpo)
    except: return 0.0

def produto_eh_relevante(nome_produto, termo_buscado):
    # O CÉREBRO NOVO: Verifica se o nome do produto tem a ver com a busca
    nome = normalizar_texto(nome_produto)
    termo = normalizar_texto(termo_buscado)
    
    # Divide a busca em palavras (ex: "iphone 13" -> "iphone", "13")
    palavras = termo.split()
    
    # Verifica se pelo menos a palavra principal está no título
    # Ex: Se buscou "iPhone", tem que ter "iphone" no titulo.
    match = 0
    for p in palavras:
        if len(p) > 2 and p in nome: # Ignora palavras pequenas como "de", "com"
            match += 1
            
    # Se encontrou pelo menos 1 palavra chave forte, aprova
    if match >= 1:
        return True
    return False

# --- CÉREBRO DE ROTEAMENTO (Mantido) ---
def identificar_lojas_para_busca(produto):
    produto = produto.lower()
    termos_tech = ['monitor', 'gamer', 'rtx', 'gtx', 'ryzen', 'intel', 'core', 'iphone', 'samsung', 'galaxy', 'xiaomi', 'ps5', 'xbox', 'notebook', 'pc', 'computador', 'teclado', 'mouse', 'headset', 'placa', 'video', 'memoria', 'ram', 'ssd', 'hd']
    termos_moda = ['tenis', 'tênis', 'camiseta', 'camisa', 'calça', 'bermuda', 'vestido', 'sapato', 'bolsa', 'mochila', 'nike', 'adidas', 'puma', 'jordan', 'mizuno']
    termos_casa = ['geladeira', 'fogao', 'fogão', 'maquina', 'lavar', 'microondas', 'ar condicionado', 'airfryer', 'liquidificador', 'batedeira']
    termos_beleza = ['perfume', 'creme', 'shampoo', 'condicionador', 'hidratante', 'boticario', 'boticário', 'maquiagem', 'base', 'batom']

    lojas = ["ml", "magalu"] # Padrão

    if any(t in produto for t in termos_tech):
        lojas.extend(["kabum", "pichau"])
        return lojas
    if any(t in produto for t in termos_moda):
        lojas.append("dafiti")
        return lojas
    if any(t in produto for t in termos_casa):
        lojas.append("brastemp")
        return lojas
    if any(t in produto for t in termos_beleza):
        lojas.append("boticario")
        return lojas

    lojas.extend(["kabum", "dafiti"]) 
    return lojas

# --- ROBÔS COM FILTRO DE RELEVÂNCIA ---

async def buscar_ml(page, produto):
    lista = []
    try:
        await page.goto(f"https://lista.mercadolivre.com.br/{produto}", timeout=15000)
        try: itens = await page.locator(".ui-search-layout__item, .poly-card").all()
        except: itens = []
        for item in itens[:15]: # Pega mais itens para filtrar depois
            try:
                if await item.locator("h2").count() > 0: titulo = await item.locator("h2").first.inner_text()
                elif await item.locator(".poly-component__title").count() > 0: titulo = await item.locator(".poly-component__title").first.inner_text()
                else: continue
                
                # FILTRO DE RELEVÂNCIA
                if not produto_eh_relevante(titulo, produto): continue

                link = await item.locator("a").first.get_attribute("href")
                if await item.locator(".andes-money-amount__fraction").count() > 0:
                    val = await item.locator(".andes-money-amount__fraction").first.inner_text()
                    preco_texto = f"R$ {val}"
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("data-src") or await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Mercado Livre"})
            except: continue
    except: pass
    return lista

async def buscar_kabum(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.kabum.com.br/busca?query={produto}", timeout=15000)
        try: itens = await page.locator("article.productCard").all()
        except: itens = []
        for item in itens[:15]:
            try:
                titulo = await item.locator("span.nameCard").first.inner_text()
                
                # FILTRO DE RELEVÂNCIA (Essencial na Kabum)
                if not produto_eh_relevante(titulo, produto): continue

                link = "https://www.kabum.com.br" + await item.locator("a").first.get_attribute("href")
                if await item.locator("span.priceCard").count() > 0: preco_texto = await item.locator("span.priceCard").first.inner_text()
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img.imageCard").count() > 0:
                    src = await item.locator("img.imageCard").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Kabum"})
            except: continue
    except: pass
    return lista

async def buscar_magalu(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.magazineluiza.com.br/busca/{produto}/", timeout=15000)
        try: itens = await page.locator('[data-testid="product-card-container"]').all()
        except: itens = []
        for item in itens[:15]:
            try:
                titulo = await item.locator('[data-testid="product-title"]').first.inner_text()
                
                if not produto_eh_relevante(titulo, produto): continue

                link_elem = item.locator("a").first
                href = await link_elem.get_attribute("href")
                link = f"https://www.magazineluiza.com.br{href}" if href.startswith("/") else href
                if await item.locator('[data-testid="price-value"]').count() > 0: preco_texto = await item.locator('[data-testid="price-value"]').first.inner_text()
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Magalu"})
            except: continue
    except: pass
    return lista

async def buscar_pichau(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.pichau.com.br/search?q={produto}", timeout=15000)
        try: itens = await page.locator('a[data-cy="list-product-link"]').all()
        except: itens = []
        for item in itens[:15]:
            try:
                txt = await item.inner_text()
                titulo = txt.split('\n')[0]
                
                if not produto_eh_relevante(titulo, produto): continue

                link = "https://www.pichau.com.br" + await item.get_attribute("href")
                import re
                match = re.search(r'R\$\s?[\d\.,]+', txt)
                if match: preco_texto = match.group(0)
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Pichau"})
            except: continue
    except: pass
    return lista

async def buscar_dafiti(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.dafiti.com.br/catalog/?q={produto}", timeout=15000)
        try: itens = await page.locator(".product-box").all()
        except: itens = []
        for item in itens[:15]:
            try:
                if await item.locator(".product-box-title").count() > 0: titulo = await item.locator(".product-box-title").first.inner_text()
                else: continue

                if not produto_eh_relevante(titulo, produto): continue

                link = await item.locator("a").first.get_attribute("href")
                if await item.locator(".product-box-price-to").count() > 0: preco_texto = await item.locator(".product-box-price-to").first.inner_text()
                elif await item.locator(".product-box-price-from").count() > 0: preco_texto = await item.locator(".product-box-price-from").first.inner_text()
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("data-original") or await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Dafiti"})
            except: continue
    except: pass
    return lista

async def buscar_boticario(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.boticario.com.br/busca/?q={produto}", timeout=15000)
        try:
            await page.wait_for_selector('a[href*="/p"]', timeout=5000)
            itens = await page.locator('a[href*="/p"]').all()
        except: itens = []
        processados = set()
        for item in itens[:15]:
            try:
                link = await item.get_attribute("href")
                if not link or link in processados: continue
                if link.startswith("/"): link = "https://www.boticario.com.br" + link
                processados.add(link)
                
                titulo = "Produto Boticário"
                if await item.locator('img').count() > 0:
                    alt = await item.locator('img').first.get_attribute("alt")
                    if alt: titulo = alt

                if not produto_eh_relevante(titulo, produto): continue

                txt = await item.inner_text()
                if "R$" not in txt: continue
                import re
                match = re.search(r'R\$\s?[\d\.,]+', txt)
                if match: preco_texto = match.group(0)
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "O Boticário"})
            except: continue
    except: pass
    return lista

async def buscar_brastemp(page, produto):
    lista = []
    try:
        await page.goto(f"https://www.brastemp.com.br/busca?q={produto}", timeout=15000)
        try:
            await page.wait_for_selector('a[href*="/p"]', timeout=5000)
            itens = await page.locator('a[href*="/p"]').all()
        except: itens = []
        processados = set()
        for item in itens[:15]:
            try:
                link = await item.get_attribute("href")
                if not link or link in processados: continue
                if link.startswith("/"): link = "https://www.brastemp.com.br" + link
                processados.add(link)
                
                titulo = "Produto Brastemp"
                if await item.locator('img').count() > 0:
                    alt = await item.locator('img').first.get_attribute("alt")
                    if alt: titulo = alt
                
                if not produto_eh_relevante(titulo, produto): continue

                txt = await item.inner_text()
                if "R$" not in txt: continue
                import re
                match = re.search(r'R\$\s?[\d\.,]+', txt)
                if match: preco_texto = match.group(0)
                else: continue
                imagem = "https://via.placeholder.com/150"
                if await item.locator("img").count() > 0:
                    src = await item.locator("img").first.get_attribute("src")
                    if src: imagem = src
                lista.append({"nome": titulo, "preco_atual": preco_texto, "preco_num": converter_preco_float(preco_texto), "link": link, "imagem": imagem, "loja": "Brastemp"})
            except: continue
    except: pass
    return lista

# --- MESTRE ---
async def buscar_todos_sites(produto_digitado):
    lista_final = []
    lojas_alvo = identificar_lojas_para_busca(produto_digitado)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        tasks = []
        if "ml" in lojas_alvo: tasks.append(buscar_ml(await context.new_page(), produto_digitado))
        if "magalu" in lojas_alvo: tasks.append(buscar_magalu(await context.new_page(), produto_digitado))
        if "kabum" in lojas_alvo: tasks.append(buscar_kabum(await context.new_page(), produto_digitado))
        if "pichau" in lojas_alvo: tasks.append(buscar_pichau(await context.new_page(), produto_digitado))
        if "dafiti" in lojas_alvo: tasks.append(buscar_dafiti(await context.new_page(), produto_digitado))
        if "boticario" in lojas_alvo: tasks.append(buscar_boticario(await context.new_page(), produto_digitado))
        if "brastemp" in lojas_alvo: tasks.append(buscar_brastemp(await context.new_page(), produto_digitado))

        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()

        for res in resultados:
            if isinstance(res, list): lista_final.extend(res)
        
        lista_final.sort(key=lambda x: x['preco_num'])
        return lista_final[:20]

async def checar_preco_link(link):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(link, timeout=20000)
            txt = await page.inner_text()
            import re
            match = re.search(r'R\$\s?[\d\.,]+', txt)
            if match: return converter_preco_float(match.group(0))
            return 0.0
        except: return 0.0
        finally: await browser.close()