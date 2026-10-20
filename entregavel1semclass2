"""
Nome: <SEU NOME AQUI>
Algoritmos e Estruturas de Dados - Rede de distribuicao
Entregavel 1: historico de periodos

Estruturas de dados e por que foram escolhidas:
- dict id -> [x, y, lucro] (registro): busca por id em O(1) esperado (ids ate 1e9, no maximo 5000 vivos); o lucro total do periodo e mantido incrementalmente.
- Kadane online (melhor intervalo): MELHOR em O(1), sem reexaminar o historico.
- list usada como pilha (pilha de prosperidade): empilhar/desempilhar O(1) amortizado.

Convencao dos comentarios das funcoes: (a) o que recebe, (b) o que faz e
devolve, (c) complexidade. n = depositos vivos, m = rotas vivas,
P = periodos registrados, h = altura da pilha.
"""
import sys


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
# REDE: operacoes da rede sobre as estruturas acima
# ======================================================================
# rede = dict com os campos:
#   T: tolerancia; registro; melhor (MelhorIntervalo); pilha (prosperidade)
# Invariantes: 
# o registro so contem depositos vivos.


def rede_nova(T):
    """(a) Tolerancia T. (b) Devolve a rede vazia. (c) Tempo O(1)."""
    rede = {"T": T, "registro": registro_novo(), "melhor": melhor_novo(),
            "pilha": pilha_nova()}
    return rede


def criar_deposito(rede, ident, x, y, lucro):
    """(a) rede; ident novo; coordenadas; lucro.
    (b) Insere o deposito no registro.
    (c) Tempo O(1) esperado."""
    registro_inserir(rede["registro"], ident, x, y, lucro)


def adicionar_rota(rede, u, v, c):
    """(a) rede; rota u -> v de custo c entre depositos vivos.
    (b) Neste estagio a rota e lida e descartada.
    (c) Tempo O(1) esperado."""
    pass


def cmd_inserir(rede, ident, x, y, lucro, rotas):
    """INSERIR. (a) rede; dados do deposito; rotas = lista de r tuplas
    (u, v, c). (b) Cria o deposito e registra as rotas; nao imprime.
    (c) Tempo O(r) esperado, mais o de criar_deposito (r <= 20)."""
    criar_deposito(rede, ident, x, y, lucro)
    for u, v, c in rotas:
        adicionar_rota(rede, u, v, c)


def cmd_lucro(rede, ident, lucro):
    """LUCRO. (a) rede; ident de deposito vivo; novo lucro.
    (b) Substitui o lucro (total ajustado pela diferenca); nao imprime.
    (c) Tempo O(1) esperado."""
    registro_mudar_lucro(rede["registro"], ident, lucro)


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
        fechar_periodo(rede, k)
    sys.stdout.write("\n".join(saida) + ("\n" if saida else ""))


if __name__ == "__main__":
    main()
