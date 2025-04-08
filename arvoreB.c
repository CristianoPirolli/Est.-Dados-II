#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define ORDER 3  // Grau mínimo da Árvore B (t), Ordem = 2*t

// Estrutura de um produto
typedef struct {
    int id;
} Produto;

// Estrutura de um nó da Árvore B
typedef struct BTreeNode {
    int n;
    Produto *chaves[2 * ORDER - 1];
    struct BTreeNode *filhos[2 * ORDER];
    int folha;
} BTreeNode;

// Estrutura da Árvore B
typedef struct {
    BTreeNode *raiz;
} BTree;

// Função para criar um novo nó da Árvore B
BTreeNode *criarNo(int folha) {
    BTreeNode *no = (BTreeNode *)malloc(sizeof(BTreeNode));
    no->folha = folha;
    no->n = 0;
    for (int i = 0; i < 2 * ORDER - 1; i++) {
        no->chaves[i] = NULL;
    }
    for (int i = 0; i < 2 * ORDER; i++) {
        no->filhos[i] = NULL;
    }
    return no;
}

// Inicializa uma Árvore B
BTree *criarArvoreB() {
    BTree *arvore = (BTree *)malloc(sizeof(BTree));
    arvore->raiz = criarNo(1);
    return arvore;
}

// Função auxiliar para imprimir a Árvore B com separação por '|'
void imprimirArvore(BTreeNode *no, int nivel) {
    if (no != NULL) {
        for (int i = no->n - 1; i >= 0; i--) {
            imprimirArvore(no->filhos[i + 1], nivel + 1);
            for (int j = 0; j < nivel * 4; j++) {
                printf(" ");
            }
            printf("| %d |\n", no->chaves[i]->id);
        }
        imprimirArvore(no->filhos[0], nivel + 1);
    }
}

// Função auxiliar para dividir um nó cheio
void dividirFilho(BTreeNode *pai, int i, BTreeNode *filho) {
    BTreeNode *novoNo = criarNo(filho->folha);
    novoNo->n = ORDER - 1;

    for (int j = 0; j < ORDER - 1; j++) {
        novoNo->chaves[j] = filho->chaves[j + ORDER];
    }

    if (!filho->folha) {
        for (int j = 0; j < ORDER; j++) {
            novoNo->filhos[j] = filho->filhos[j + ORDER];
        }
    }

    filho->n = ORDER - 1;

    for (int j = pai->n; j >= i + 1; j--) {
        pai->filhos[j + 1] = pai->filhos[j];
    }
    pai->filhos[i + 1] = novoNo;

    for (int j = pai->n - 1; j >= i; j--) {
        pai->chaves[j + 1] = pai->chaves[j];
    }

    pai->chaves[i] = filho->chaves[ORDER - 1];
    pai->n++;
}

// Função para buscar um produto na árvore (para verificar duplicidade)
BTreeNode *buscarProduto(BTreeNode *no, int id) {
    int i = 0;
    while (i < no->n && id > no->chaves[i]->id) {
        i++;
    }

    if (i < no->n && id == no->chaves[i]->id) {
        return no; // Produto encontrado neste nó
    }

    if (no->folha) {
        return NULL; // Produto não encontrado
    }

    return buscarProduto(no->filhos[i], id);
}

// Função auxiliar para inserir em um nó não cheio
void inserirNaoCheio(BTreeNode *no, Produto *produto) {
    int i = no->n - 1;
    if (no->folha) {
        while (i >= 0 && produto->id < no->chaves[i]->id) {
            no->chaves[i + 1] = no->chaves[i];
            i--;
        }
        no->chaves[i + 1] = produto;
        no->n++;
    } else {
        while (i >= 0 && produto->id < no->chaves[i]->id) {
            i--;
        }
        i++;
        if (no->filhos[i]->n == (2 * ORDER - 1)) {
            dividirFilho(no, i, no->filhos[i]);
            if (produto->id > no->chaves[i]->id) {
                i++;
            }
        }
        inserirNaoCheio(no->filhos[i], produto);
    }
}

// Função para inserir um produto na Árvore B
void inserirProduto(BTree *arvore, Produto *produto) {
    if (!arvore || !produto) return;

    if (buscarProduto(arvore->raiz, produto->id)) {
        printf("Erro: Produto com ID %d já existe na árvore.\n", produto->id);
        free(produto); // Libera a memória do produto duplicado
        return;
    }

    BTreeNode *raiz = arvore->raiz;
    if (raiz->n == (2 * ORDER - 1)) {
        BTreeNode *novoNo = criarNo(0);
        arvore->raiz = novoNo;
        novoNo->filhos[0] = raiz;
        dividirFilho(novoNo, 0, raiz);
        inserirNaoCheio(novoNo, produto);
    } else {
        inserirNaoCheio(raiz, produto);
    }
}

// Função para inserir produtos aleatórios sem repetição
void inserirProdutosAleatorios(BTree *arvore, int num_produtos) {
    if (!arvore || num_produtos <= 0) return;
    srand(time(NULL));
    int inseridos = 0;
    while (inseridos < num_produtos) {
        Produto *p = (Produto *)malloc(sizeof(Produto));
        if (!p) {
            perror("Erro ao alocar memória para produto aleatório");
            break;
        }
        p->id = rand() % 1000000000001; // IDs de 0 a 1.000.000.000.000
        if (!buscarProduto(arvore->raiz, p->id)) {
            inserirProduto(arvore, p);
            inseridos++;
        } else {
            free(p); // Libera a memória do produto duplicado
        }
    }
    printf("Inseridos %d produtos aleatórios únicos.\n", inseridos);
}

// Função para encontrar o índice da primeira chave maior ou igual a k em um nó
int encontrarIndice(BTreeNode *no, int k) {
    int i = 0;
    while (i < no->n && no->chaves[i]->id < k) {
        i++;
    }
    return i;
}

// Função para remover uma chave de um nó folha
void removerDeFolha(BTreeNode *no, int idx) {
    for (int i = idx + 1; i < no->n; i++) {
        no->chaves[i - 1] = no->chaves[i];
    }
    no->n--;
}

// Função para remover uma chave de um nó não folha
void removerDeNaoFolha(BTreeNode *no, int idx) {
    int k = no->chaves[idx]->id;

    if (no->filhos[idx]->n >= ORDER) {
        BTreeNode *pred = no->filhos[idx];
        Produto *predecessor = pred->chaves[pred->n - 1];
        no->chaves[idx] = predecessor;
        removerProdutoRecursivo(no->filhos[idx], predecessor->id);
    } else if (no->filhos[idx + 1]->n >= ORDER) {
        BTreeNode *suc = no->filhos[idx + 1];
        Produto *sucessor = suc->chaves[0];
        no->chaves[idx] = sucessor;
        removerProdutoRecursivo(no->filhos[idx + 1], sucessor->id);
    } else {
        fundirFilhos(no, idx);
        removerProdutoRecursivo(no->filhos[idx], k);
    }
}

// Função para preencher um filho com menos de ORDER - 1 chaves
void preencher(BTreeNode *no, int idx) {
    if (idx != 0 && no->filhos[idx - 1]->n >= ORDER) {
        emprestarAnterior(no, idx);
    } else if (idx != no->n && no->filhos[idx + 1]->n >= ORDER) {
        emprestarProximo(no, idx);
    } else {
        if (idx != no->n) {
            fundirFilhos(no, idx);
        } else {
            fundirFilhos(no, idx - 1);
        }
    }
}

// Função para emprestar uma chave do filho anterior
void emprestarAnterior(BTreeNode *no, int idx) {
    BTreeNode *filho = no->filhos[idx];
    BTreeNode *irmao = no->filhos[idx - 1];

    for (int i = filho->n - 1; i >= 0; i--) {
        filho->filhos[i + 1] = filho->filhos[i];
    }
    filho->filhos[0] = irmao->filhos[irmao->n];

    for (int i = filho->n - 1; i >= 0; i--) {
        filho->chaves[i + 1] = filho->chaves[i];
    }
    filho->chaves[0] = no->chaves[idx - 1];

    no->chaves[idx - 1] = irmao->chaves[irmao->n - 1];

    filho->n++;
    irmao->n--;
}

// Função para emprestar uma chave do próximo filho
void emprestarProximo(BTreeNode *no, int idx) {
    BTreeNode *filho = no->filhos[idx];
    BTreeNode *irmao = no->filhos[idx + 1];

    filho->chaves[filho->n] = no->chaves[idx];

    if (!filho->folha) {
        filho->filhos[filho->n + 1] = irmao->filhos[0];
    }

    no->chaves[idx] = irmao->chaves[0];

    for (int i = 1; i < irmao->n; i++) {
        irmao->chaves[i - 1] = irmao->chaves[i];
    }

    if (!irmao->folha) {
        for (int i = 1; i <= irmao->n; i++) {
            irmao->filhos[i - 1] = irmao->filhos[i];
        }
    }

    filho->n++;
    irmao->n--;
}

// Função para fundir o filho idx com seu próximo irmão
void fundirFilhos(BTreeNode *no, int idx) {
    BTreeNode *filho = no->filhos[idx];
    BTreeNode *irmao = no->filhos[idx + 1];

    filho->chaves[ORDER - 1] = no->chaves[idx];

    for (int i = 0; i < irmao->n; i++) {
        filho->chaves[i + ORDER] = irmao->chaves[i];
    }

    if (!filho->folha) {
        for (int i = 0; i <= irmao->n; i++) {
            filho->filhos[i + ORDER] = irmao->filhos[i];
        }
    }

    filho->n += irmao->n + 1;

    for (int i = idx + 1; i < no->n; i++) {
        no->chaves[i - 1] = no->chaves[i];
        no->filhos[i] = no->filhos[i + 1];
    }

    no->n--;
    free(irmao);
}

// Função recursiva para remover um produto da Árvore B
void removerProdutoRecursivo(BTreeNode *no, int id) {
    int idx = encontrarIndice(no, id);
    Produto *chave_encontrada = (idx < no->n && no->chaves[idx] && no->chaves[idx]->id == id) ? no->chaves[idx] : NULL;

    if (chave_encontrada) {
        if (no->folha) {
            removerDeFolha(no, idx);
        } else {
            removerDeNaoFolha(no, idx);
        }
    } else {
        if (no->folha) {
            printf("Produto com ID %d não encontrado na árvore.\n", id);
            return;
        }

        int flag = (idx == no->n);

        if (no->filhos[idx]->n < ORDER) {
            preencher(no, idx);
        }

        if (flag && idx > no->n) {
            removerProdutoRecursivo(no->filhos[idx - 1], id);
        } else {
            removerProdutoRecursivo(no->filhos[idx], id);
        }
    }
}

// Função para remover um produto da Árvore B
void removerProduto(BTree *arvore, int id) {
    if (!arvore->raiz) {
        printf("Árvore vazia.\n");
        return;
    }
    removerProdutoRecursivo(arvore->raiz, id);
    if (arvore->raiz->n == 0) {
        BTreeNode *tmp = arvore->raiz;
        if (!arvore->raiz->folha) {
            arvore->raiz = arvore->raiz->filhos[0];
        } else {
            arvore->raiz = NULL;
        }
        free(tmp);
    }
    printf("Removendo o produto com ID %d\n", id);
}

// Função para exibir menu e interagir com o usuário
void menu(BTree *arvore) {
    int opcao;
    int num_aleatorios; // Variável para armazenar a quantidade desejada

    do {
        printf("\nMENU:\n");
        printf("1. Inserir produto\n");
        printf("2. Inserir produtos aleatórios\n");
        printf("   Digite a quantidade desejada:\n");
        printf("3. Imprimir árvore\n");
        printf("4. Remover produto\n");
        printf("5. Sair\n");
        printf("Escolha uma opção: ");
        scanf("%d", &opcao);

        if (opcao == 1) {
            Produto *p = (Produto *)malloc(sizeof(Produto));
            if (!p) {
                perror("Erro ao alocar memória para produto");
                continue;
            }
            printf("Digite o ID do produto: ");
            scanf("%d", &p->id);
            inserirProduto(arvore, p);
        } else if (opcao == 2) {
            printf("Quantidade de produtos aleatórios a inserir: ");
            if (scanf("%d", &num_aleatorios) == 1 && num_aleatorios > 0) {
                inserirProdutosAleatorios(arvore, num_aleatorios);
            } else {
                printf("Entrada inválida para a quantidade.\n");
                // Limpar o buffer de entrada em caso de erro
                while (getchar() != '\n');
            }
        } else if (opcao == 3) {
            imprimirArvore(arvore->raiz, 0);
        } else if (opcao == 4) {
            int id;
            printf("Digite o ID do produto a remover: ");
            scanf("%d", &id);
            removerProduto(arvore, id);
        } else if (opcao == 5) {
            printf("Saindo...\n");
        } else {
            printf("Opção inválida.\n");
        }
    } while (opcao != 5);
}

// Função principal
int main() {
    BTree *arvore = criarArvoreB();
    menu(arvore);
    return 0;
}