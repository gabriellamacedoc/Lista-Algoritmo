"""
Nome: Ana Clara de Lira Florentino e Silva, Júlia Lavínia Rodrigues Pedrosa de Carvalho e Maria Gabriella Macedo Cardoso
Algoritmos e Estruturas de Dados - Rede de distribuicao
Entregavel 3: rede de rotas

Estruturas de dados e por que foram escolhidas:
- dict id -> [x, y, lucro] (registro): busca por id em O(1) esperado; lucro total incremental.
- Kadane online (melhor intervalo) e pilha de prosperidade (list), do Entregavel 1.
- Min-heap binario indexado proprio (fila de prioridade): REMOVER (E2) e Dijkstra (E3) a reutilizam.
- Divisao e conquista (par mais proximo), do Entregavel 2, com cache do ultimo resultado.
- Grafo dirigido esparso (dict de dict + indice reverso de entrada): INSERIR e remocao de no em O(grau); Dijkstra com decrease-key.

Convencao dos comentarios das funcoes: (a) o que recebe, (b) o que faz e
devolve, (c) complexidade. n = depositos vivos, m = rotas vivas,
P = periodos registrados, h = altura da pilha.
"""
import sys
from math import isqrt


# ======================================================================
# REGISTRO DE DEPOSITOS
# ======================================================================
# Estrutura (biblioteca): dict (tabela hash). Operacoes get/set/del em
# O(1) esperado (hipotese: hash uniforme). Escolhida porque os ids chegam
# a 10^9 (vetor direto inviavel) e ha no maximo 5000 vivos.
#
# registro = {"dados": {...}, "total": int}
#   dados: id -> [x, y, lucro]; as chaves sao exatamente os depositos vivos.
#   total: soma dos lucros de todos os depositos vivos (inclusive os abaixo
#          da tolerancia ainda nao removidos).
# Invariante: total == soma dos lucros em dados, mantido por diferenca
# (nunca se varre o registro para obter o lucro do periodo).


def registro_novo():
    """(a) Nao recebe nada. (b) Devolve um registro vazio.
    (c) Tempo O(1); espaco O(1)."""
    return {"dados": {}, "total": 0}


def registro_inserir(registro, ident, x, y, lucro):
    """(a) registro; ident ainda nao vivo; coordenadas x, y; lucro inicial.
    (b) Cria o deposito e soma seu lucro em total. Nao devolve nada.
    (c) Tempo O(1) esperado (insercao em hash)."""
    registro["dados"][ident] = [x, y, lucro]
    registro["total"] += lucro


def registro_mudar_lucro(registro, ident, lucro):
    """(a) registro; ident de deposito vivo; novo lucro (substitui o antigo).
    (b) Atualiza o lucro e ajusta total pela diferenca. Nao devolve nada.
    (c) Tempo O(1) esperado (busca em hash)."""
    d = registro["dados"][ident]
    registro["total"] += lucro - d[2]
    d[2] = lucro


def registro_remover(registro, ident):
    """(a) registro; ident de deposito vivo.
    (b) Elimina o deposito e subtrai seu lucro de total. Nao devolve nada.
    (c) Tempo O(1) esperado (remocao em hash)."""
    d = registro["dados"].pop(ident)
    registro["total"] -= d[2]


# ======================================================================
# HISTORICO: MELHOR INTERVALO (Kadane online) E PILHA DE PROSPERIDADE
# ======================================================================
# melhor = {"fim_soma", "fim_ini", "melhor"}
#   fim_soma, fim_ini: maior soma de um intervalo que termina no ultimo
#       periodo registrado e o menor inicio que a atinge.
#   melhor: tupla (i, j, S) do melhor intervalo global, ou None se vazio.
# Invariante: apos registrar o periodo k, fim_* descreve o melhor intervalo
# terminando em k (menor i nos empates) e "melhor" e o otimo sobre [1..k],
# com desempate por menor i e depois menor j. Espaco O(1): nao guarda o
# historico de lucros.
#
# pilha = {"itens": [[j, r], ...], "soma": int}   (list usada como pilha)
#   itens: base = ganho mais antigo, topo = mais recente; r > 0 sempre.
#   soma: soma dos residuos.
# Invariantes: todo r > 0; os j sao estritamente crescentes da base ao
# topo; soma == soma dos r; se nao vazia e b e o periodo da base, entao
# soma = Lb + ... + Lk.


def melhor_novo():
    """(a) Nada. (b) Devolve o estado vazio do melhor intervalo.
    (c) Tempo O(1)."""
    return {"fim_soma": 0, "fim_ini": 0, "melhor": None}


def melhor_registrar(mi, k, lucro):
    """(a) mi; k (proximo periodo, consecutivo); lucro Lk.
    (b) Estende o intervalo anterior se sua soma for >= 0 (no empate prefere
    o menor inicio), senao recomeca em k; atualiza o melhor global so se a
    soma for maior, ou igual com inicio menor (assim o menor j e mantido).
    (c) Tempo O(1); espaco O(1)."""
    if k > 1 and mi["fim_soma"] >= 0:
        mi["fim_soma"] += lucro
    else:
        mi["fim_soma"] = lucro
        mi["fim_ini"] = k
    b = mi["melhor"]
    if b is None or mi["fim_soma"] > b[2] or (
            mi["fim_soma"] == b[2] and mi["fim_ini"] < b[0]):
        mi["melhor"] = (mi["fim_ini"], k, mi["fim_soma"])


def melhor_consultar(mi):
    """(a) mi com pelo menos um periodo registrado.
    (b) Devolve a linha "i j S" do melhor intervalo dos periodos ja
    registrados. (c) Tempo O(1)."""
    i, j, s = mi["melhor"]
    return "%d %d %d" % (i, j, s)


def pilha_nova():
    """(a) Nada. (b) Devolve uma pilha de prosperidade vazia. (c) O(1)."""
    return {"itens": [], "soma": 0}


def pilha_registrar(pilha, k, lucro):
    """(a) pilha; periodo k; lucro Lk do periodo.
    (b) Lk > 0 empilha [k, Lk]; Lk = 0 nao muda; Lk < 0 compensa
    d = -Lk consumindo topos (reduz o topo ou o desempilha), descartando a
    sobra se a pilha esvaziar. (c) Tempo O(1) amortizado: cada elemento e
    empilhado uma vez e desempilhado no maximo uma vez (uma chamada isolada
    pode custar O(h))."""
    itens = pilha["itens"]
    if lucro > 0:
        itens.append([k, lucro])
        pilha["soma"] += lucro
    elif lucro < 0:
        d = -lucro
        while d > 0 and itens:
            topo = itens[-1]
            if topo[1] > d:
                topo[1] -= d
                pilha["soma"] -= d
                d = 0
            else:
                itens.pop()
                pilha["soma"] -= topo[1]
                d -= topo[1]


def pilha_consultar(pilha):
    """(a) pilha. (b) Devolve "0" se vazia; senao "h b s i r": altura,
    periodo da base, soma dos residuos, periodo e residuo do topo.
    (c) Tempo O(1)."""
    itens = pilha["itens"]
    if not itens:
        return "0"
    i, r = itens[-1]
    return "%d %d %d %d %d" % (len(itens), itens[0][0], pilha["soma"], i, r)


# ======================================================================
# FILA DE PRIORIDADE COM ALTERACAO DE CHAVE: min-heap binario indexado
# ======================================================================
# fila = {"chaves": [...], "ids": [...], "pos": {...}}
#   chaves: chaves na ordem do heap.
#   ids:    identificadores, em lista paralela a "chaves".
#   pos:    dict id -> indice do id em ids/chaves.
# Invariantes: chaves[(i-1)//2] <= chaves[i] (propriedade de heap);
# ids[pos[d]] == d para todo d presente; ids sem repeticao.
# O indice "pos" permite alterar a chave de um id em O(log n), o que o
# heapq da biblioteca nao oferece.


def fila_nova():
    """(a) Nada. (b) Devolve uma fila vazia. (c) O(1)."""
    return {"chaves": [], "ids": [], "pos": {}}


def fila_subir(fila, i):
    """(a) fila; indice i valido, cujo elemento pode estar menor que o pai.
    (b) Sobe o elemento ate restaurar a propriedade de heap, atualizando pos.
    (c) Tempo O(log n) no pior caso (altura do heap)."""
    chaves, ids, pos = fila["chaves"], fila["ids"], fila["pos"]
    k, d = chaves[i], ids[i]
    while i > 0:
        p = (i - 1) >> 1
        if chaves[p] <= k:
            break
        chaves[i] = chaves[p]
        ids[i] = ids[p]
        pos[ids[i]] = i
        i = p
    chaves[i] = k
    ids[i] = d
    pos[d] = i


def fila_descer(fila, i):
    """(a) fila; indice i valido, cujo elemento pode estar maior que um filho.
    (b) Desce o elemento ate restaurar a propriedade de heap, atualizando pos.
    (c) Tempo O(log n) no pior caso."""
    chaves, ids, pos = fila["chaves"], fila["ids"], fila["pos"]
    n = len(ids)
    k, d = chaves[i], ids[i]
    while True:
        c = 2 * i + 1
        if c >= n:
            break
        if c + 1 < n and chaves[c + 1] < chaves[c]:
            c += 1
        if chaves[c] >= k:
            break
        chaves[i] = chaves[c]
        ids[i] = ids[c]
        pos[ids[i]] = i
        i = c
    chaves[i] = k
    ids[i] = d
    pos[d] = i


def fila_inserir(fila, ident, chave):
    """(a) fila; ident ausente da fila; sua chave.
    (b) Insere no fim e sobe. (c) Tempo O(log n) no pior caso."""
    fila["chaves"].append(chave)
    fila["ids"].append(ident)
    fila_subir(fila, len(fila["ids"]) - 1)


def fila_atualizar(fila, ident, chave):
    """(a) fila; ident presente; nova chave.
    (b) Troca a chave e restaura o heap subindo (se diminuiu) ou descendo
    (se aumentou). (c) Tempo O(log n) no pior caso."""
    i = fila["pos"][ident]
    antiga = fila["chaves"][i]
    fila["chaves"][i] = chave
    if chave < antiga:
        fila_subir(fila, i)
    elif chave > antiga:
        fila_descer(fila, i)


def fila_minimo(fila):
    """(a) fila nao vazia. (b) Devolve (chave, id) minimos sem remover.
    (c) Tempo O(1)."""
    return fila["chaves"][0], fila["ids"][0]


def fila_extrair_min(fila):
    """(a) fila nao vazia. (b) Remove e devolve (chave, id) minimos: move o
    ultimo elemento para a raiz e desce. (c) Tempo O(log n)."""
    chaves, ids, pos = fila["chaves"], fila["ids"], fila["pos"]
    k0, d0 = chaves[0], ids[0]
    ck = chaves.pop()
    cd = ids.pop()
    del pos[d0]
    if ids:
        chaves[0] = ck
        ids[0] = cd
        pos[cd] = 0
        fila_descer(fila, 0)
    return k0, d0


# ======================================================================
# PAR MAIS PROXIMO: divisao e conquista
# ======================================================================


def par_mais_proximo(pontos):
    """(a) Lista de tuplas (x, y, id) com >= 2 pontos de coordenadas
    distintas.
    (b) Devolve (d2, a, b): menor distancia ao quadrado (inteira, exata) e
    os ids a < b do par. Nenhuma distancia entre pares e armazenada alem do
    melhor corrente. Algoritmo: ordena por x; divide ao meio; cada metade
    devolve seus pontos ordenados por y (como no merge sort); na faixa
    vertical de largura sqrt(melhor) em torno da divisoria, cada ponto so e
    comparado com os seguintes (em y) cuja diferenca de y ainda e < sqrt do
    melhor (O(1) pontos, argumento de empacotamento).
    (c) Tempo O(n log n) no pior caso (T(n) = 2T(n/2) + O(n)).
    Espaco adicional O(n)."""
    P = sorted(pontos)
    melhor = [1 << 100, 0, 0]

    def rec(lo, hi):
        if hi - lo <= 3:
            for i in range(lo, hi):
                xi, yi, di = P[i]
                for j in range(i + 1, hi):
                    dx = P[j][0] - xi
                    dy = P[j][1] - yi
                    d = dx * dx + dy * dy
                    if d < melhor[0]:
                        melhor[0], melhor[1], melhor[2] = d, di, P[j][2]
            return sorted(P[lo:hi], key=lambda p: p[1])
        mid = (lo + hi) >> 1
        xm = P[mid][0]
        esq = rec(lo, mid)
        dir_ = rec(mid, hi)
        ordenado = sorted(esq + dir_, key=lambda p: p[1])  # 2 runs: O(n)
        faixa = [p for p in ordenado if (p[0] - xm) ** 2 < melhor[0]]
        nf = len(faixa)
        for i in range(nf):
            xi, yi, di = faixa[i]
            for j in range(i + 1, nf):
                xj, yj, dj = faixa[j]
                dy = yj - yi
                if dy * dy >= melhor[0]:
                    break
                dx = xj - xi
                d = dx * dx + dy * dy
                if d < melhor[0]:
                    melhor[0], melhor[1], melhor[2] = d, di, dj
        return ordenado

    rec(0, len(P))
    a, b = melhor[1], melhor[2]
    if a > b:
        a, b = b, a
    return melhor[0], a, b


def teto_raiz(d2):
    """(a) d2 >= 0 inteiro. (b) Devolve o menor inteiro t com t*t >= d2,
    usando aritmetica inteira (math.isqrt). (c) Tempo O(1) para 64 bits."""
    r = isqrt(d2)
    return r if r * r == d2 else r + 1


# ======================================================================
# GRAFO DE ROTAS: dirigido, dinamico, esparso
# ======================================================================
# grafo = {"saida": {u: {v: custo}}, "entrada": {v: {u, ...}}}
#   saida:   para cada no u, as rotas que saem dele (dict destino -> custo).
#   entrada: para cada no v, o conjunto (set) dos u com rota u -> v
#            (indice reverso, para remover um no sem varrer o grafo todo).
# Invariantes: v em saida[u]  <=>  u em entrada[v]; toda chave e um deposito
# vivo; sem lacos nem rotas duplicadas. Espaco O(n + m).
# dict/set da biblioteca: inserir/buscar/remover O(1) esperado (hash).


def grafo_novo():
    """(a) Nada. (b) Devolve um grafo vazio. (c) O(1)."""
    return {"saida": {}, "entrada": {}}


def grafo_adicionar_no(grafo, ident):
    """(a) grafo; ident novo. (b) Cria um no isolado.
    (c) Tempo O(1) esperado."""
    grafo["saida"][ident] = {}
    grafo["entrada"][ident] = set()


def grafo_adicionar_rota(grafo, u, v, c):
    """(a) grafo; nos vivos u e v; custo c >= 1.
    (b) Cria a rota u -> v (se ja existir, substitui o custo).
    (c) Tempo O(1) esperado."""
    grafo["saida"][u][v] = c
    grafo["entrada"][v].add(u)


def grafo_remover_no(grafo, ident):
    """(a) grafo; no vivo ident.
    (b) Remove o no e todas as rotas que entram ou saem dele, nos dois
    indices. (c) Tempo O(grau de entrada + grau de saida) esperado."""
    for w in grafo["saida"].pop(ident):
        grafo["entrada"][w].discard(ident)
    for u in grafo["entrada"].pop(ident):
        del grafo["saida"][u][ident]


def dijkstra(grafo, s):
    """(a) grafo (custos >= 1) e no de origem s (vivo).
    (b) Devolve dict no -> menor custo, para os nos alcancaveis (inclui s,
    com 0). Usa a fila de prioridade indexada com decrease-key: cada no
    entra na fila no maximo uma vez.
    (c) Tempo O((n + m) log n); espaco O(n)."""
    dist = {s: 0}
    fila = fila_nova()
    fila_inserir(fila, s, 0)
    saida = grafo["saida"]
    while fila["ids"]:
        d, u = fila_extrair_min(fila)
        for v, c in saida[u].items():
            nd = d + c
            od = dist.get(v)
            if od is None:
                dist[v] = nd
                fila_inserir(fila, v, nd)
            elif nd < od:
                dist[v] = nd
                fila_atualizar(fila, v, nd)
    return dist


# ======================================================================
# REDE: operacoes da rede sobre as estruturas acima
# ======================================================================
# rede = dict com os campos:
#   T: tolerancia; registro; melhor (MelhorIntervalo); pilha (prosperidade)
#   fila: fila de prioridade (chave = lucro), um elemento por deposito vivo
#   par_cache: ultimo resultado de PAR (d2, a, b), ou None se invalido
#   grafo: grafo de rotas
# Invariantes: ids da fila == chaves de registro["dados"] e cada chave == lucro atual;
# par_cache so e nao-None enquanto o conjunto de vivos nao mudou; nos do
# grafo == depositos vivos; 
# o registro so contem depositos vivos.


def rede_nova(T):
    """(a) Tolerancia T. (b) Devolve a rede vazia. (c) Tempo O(1)."""
    rede = {"T": T, "registro": registro_novo(), "melhor": melhor_novo(),
            "pilha": pilha_nova(), "fila": fila_nova(),
            "par_cache": None, "grafo": grafo_novo()}
    return rede


def criar_deposito(rede, ident, x, y, lucro):
    """(a) rede; ident novo; coordenadas; lucro.
    (b) Insere o deposito no registro, na fila (e invalida o cache de PAR) e no grafo.
    (c) Tempo O(log n)."""
    registro_inserir(rede["registro"], ident, x, y, lucro)
    fila_inserir(rede["fila"], ident, lucro)
    rede["par_cache"] = None
    grafo_adicionar_no(rede["grafo"], ident)


def adicionar_rota(rede, u, v, c):
    """(a) rede; rota u -> v de custo c entre depositos vivos.
    (b) Insere a rota no grafo.
    (c) Tempo O(1) esperado."""
    grafo_adicionar_rota(rede["grafo"], u, v, c)


def cmd_inserir(rede, ident, x, y, lucro, rotas):
    """INSERIR. (a) rede; dados do deposito; rotas = lista de r tuplas
    (u, v, c). (b) Cria o deposito e registra as rotas; nao imprime.
    (c) Tempo O(r) esperado, mais o de criar_deposito (r <= 20)."""
    criar_deposito(rede, ident, x, y, lucro)
    for u, v, c in rotas:
        adicionar_rota(rede, u, v, c)


def cmd_lucro(rede, ident, lucro):
    """LUCRO. (a) rede; ident de deposito vivo; novo lucro.
    (b) Substitui o lucro no registro e a chave na fila (o conjunto de vivos nao muda, entao o cache de PAR continua valido); nao imprime.
    (c) Tempo O(log n)."""
    registro_mudar_lucro(rede["registro"], ident, lucro)
    fila_atualizar(rede["fila"], ident, lucro)


def cmd_melhor(rede):
    """MELHOR. (a) rede. (b) Devolve "i j S" sobre os periodos ja
    registrados. (c) Tempo O(1) (resposta mantida online por Kadane)."""
    return melhor_consultar(rede["melhor"])


def cmd_prosperidade(rede):
    """PROSPERIDADE. (a) rede. (b) Devolve a linha da pilha apos o ultimo
    periodo registrado. (c) Tempo O(1)."""
    return pilha_consultar(rede["pilha"])


def fechar_periodo(rede, k):
    """(a) rede; numero k do periodo que acabou de terminar.
    (b) Le Lk = registro["total"] (sem varrer depositos) e o registra no
    melhor intervalo e na pilha de prosperidade.
    (c) Tempo O(1) amortizado (a pilha pode desempilhar varios elementos,
    pagos pelos empilhamentos)."""
    L = rede["registro"]["total"]
    melhor_registrar(rede["melhor"], k, L)
    pilha_registrar(rede["pilha"], k, L)


def eliminar_deposito(rede, ident):
    """(a) rede; ident de deposito vivo, ja retirado da fila.
    (b) Remove o deposito de todas as estruturas que o mencionam: registro e grafo (com suas rotas) e invalida o cache de PAR.
    (c) Tempo O(grau) esperado."""
    registro_remover(rede["registro"], ident)
    grafo_remover_no(rede["grafo"], ident)
    rede["par_cache"] = None


def cmd_remover(rede):
    """REMOVER. (a) rede.
    (b) Fecha todo deposito com lucro < T extraindo o minimo da fila
    enquanto a chave for < T (os demais nunca sao examinados). Devolve a
    quantidade removida, como texto.
    (c) Tempo O((k + 1) log n) para k removidos, mais o grau das rotas."""
    fila = rede["fila"]
    cont = 0
    while fila["ids"] and fila_minimo(fila)[0] < rede["T"]:
        _, ident = fila_extrair_min(fila)
        eliminar_deposito(rede, ident)
        cont += 1
    return str(cont)


def cmd_par(rede):
    """PAR. (a) rede com >= 2 depositos vivos.
    (b) Devolve "a b d": a < b sao os ids do par mais proximo e d a
    distancia euclidiana arredondada para cima. Reutiliza o ultimo
    resultado se os vivos nao mudaram.
    (c) Tempo O(n log n) (divisao e conquista); O(1) com cache.
    Espaco O(n)."""
    if rede["par_cache"] is None:
        pts = [(d[0], d[1], i) for i, d in rede["registro"]["dados"].items()]
        rede["par_cache"] = par_mais_proximo(pts)
    d2, a, b = rede["par_cache"]
    return "%d %d %d" % (a, b, teto_raiz(d2))


def cmd_dist(rede, s):
    """DIST. (a) rede; s deposito vivo.
    (b) Devolve a linha com o menor custo de s a cada outro deposito vivo,
    em ordem crescente de id; -1 se inalcancavel; linha vazia se s e o unico.
    (c) Tempo O((n + m) log n) (Dijkstra) + O(n log n) para ordenar os ids.
    Espaco O(n)."""
    dist = dijkstra(rede["grafo"], s)
    return " ".join(str(dist.get(i, -1)) for i in sorted(rede["registro"]["dados"])
                    if i != s)


# ======================================================================
# PONTO DE ANCORAGEM
# ======================================================================


def main():
    """(a) Nada (le a entrada padrao, no formato do enunciado).
    (b) Faz o setup, executa os lotes na ordem e escreve uma linha por
    operacao que imprime. As rotas sao sempre lidas.
    (c) Tempo: soma do custo das operacoes tratadas (ver as funcoes cmd_*);
    leitura e despacho sao O(tamanho da entrada). Espaco O(entrada)."""
    tk = sys.stdin.buffer.read().split()
    n, m, T = int(tk[0]), int(tk[1]), int(tk[2])
    pos = 3
    rede = rede_nova(T)
    for _ in range(n):
        criar_deposito(rede, int(tk[pos]), int(tk[pos + 1]),
                       int(tk[pos + 2]), int(tk[pos + 3]))
        pos += 4
    for _ in range(m):
        adicionar_rota(rede, int(tk[pos]), int(tk[pos + 1]), int(tk[pos + 2]))
        pos += 3
    P = int(tk[pos])
    pos += 1
    fechar_periodo(rede, 1)
    saida = []
    for k in range(2, P + 2):
        q = int(tk[pos])
        pos += 1
        for _ in range(q):
            op = tk[pos]
            pos += 1
            if op == b"LUCRO":
                cmd_lucro(rede, int(tk[pos]), int(tk[pos + 1]))
                pos += 2
            elif op == b"INSERIR":
                ident, x, y, L, r = (int(t) for t in tk[pos:pos + 5])
                pos += 5
                rotas = [(int(tk[pos + 3 * i]), int(tk[pos + 3 * i + 1]),
                          int(tk[pos + 3 * i + 2])) for i in range(r)]
                pos += 3 * r
                cmd_inserir(rede, ident, x, y, L, rotas)
            elif op == b"MELHOR":
                saida.append(cmd_melhor(rede))
            elif op == b"PROSPERIDADE":
                saida.append(cmd_prosperidade(rede))
            elif op == b"REMOVER":
                saida.append(cmd_remover(rede))
            elif op == b"PAR":
                saida.append(cmd_par(rede))
            elif op == b"DIST":
                saida.append(cmd_dist(rede, int(tk[pos])))
                pos += 1
        fechar_periodo(rede, k)
    sys.stdout.write("\n".join(saida) + ("\n" if saida else ""))


if __name__ == "__main__":
    main()
