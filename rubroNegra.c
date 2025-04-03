#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define VERMELHO 1
#define PRETO 0

// Estrutura do nó da árvore Rubro-Negra
typedef struct Node {
    int matricula;
    char nome[100];
    int cor;
    struct Node *esquerda, *direita, *pai;
} Node;

// Função para criar um novo nó
Node* criarNo(int matricula, char nome[], Node* pai) {
    Node* novoNo = (Node*)malloc(sizeof(Node));
    novoNo->matricula = matricula;
    strcpy(novoNo->nome, nome);
    novoNo->cor = VERMELHO;
    novoNo->esquerda = novoNo->direita = NULL;
    novoNo->pai = pai;
    return novoNo;
}

// Rotação à esquerda
Node* rotacaoEsquerda(Node* raiz, Node* x) {
    Node* y = x->direita;
    x->direita = y->esquerda;
    if (y->esquerda) y->esquerda->pai = x;
    y->pai = x->pai;
    if (!x->pai)
        raiz = y;
    else if (x == x->pai->esquerda)
        x->pai->esquerda = y;
    else
        x->pai->direita = y;
    y->esquerda = x;
    x->pai = y;
    return raiz;
}

// Rotação à direita
Node* rotacaoDireita(Node* raiz, Node* y) {
    Node* x = y->esquerda;
    y->esquerda = x->direita;
    if (x->direita) x->direita->pai = y;
    x->pai = y->pai;
    if (!y->pai)
        raiz = x;
    else if (y == y->pai->direita)
        y->pai->direita = x;
    else
        y->pai->esquerda = x;
    x->direita = y;
    y->pai = x;
    return raiz;
}

// Ajuste após inserção
Node* balancearInsercao(Node* raiz, Node* novoNo) {
    while (novoNo->pai && novoNo->pai->cor == VERMELHO) {
        Node* avo = novoNo->pai->pai;
        if (!avo) break;
        if (novoNo->pai == avo->esquerda) {
            Node* tio = avo->direita;
            if (tio && tio->cor == VERMELHO) {
                novoNo->pai->cor = PRETO;
                tio->cor = PRETO;
                avo->cor = VERMELHO;
                novoNo = avo;
            } else {
                if (novoNo == novoNo->pai->direita) {
                    novoNo = novoNo->pai;
                    raiz = rotacaoEsquerda(raiz, novoNo);
                }
                novoNo->pai->cor = PRETO;
                avo->cor = VERMELHO;
                raiz = rotacaoDireita(raiz, avo);
            }
        } else {
            Node* tio = avo->esquerda;
            if (tio && tio->cor == VERMELHO) {
                novoNo->pai->cor = PRETO;
                tio->cor = PRETO;
                avo->cor = VERMELHO;
                novoNo = avo;
            } else {
                if (novoNo == novoNo->pai->esquerda) {
                    novoNo = novoNo->pai;
                    raiz = rotacaoDireita(raiz, novoNo);
                }
                novoNo->pai->cor = PRETO;
                avo->cor = VERMELHO;
                raiz = rotacaoEsquerda(raiz, avo);
            }
        }
    }
    raiz->cor = PRETO;
    return raiz;
}

// Inserção de um nó na árvore
Node* inserir(Node* raiz, int matricula, char nome[]) {
    Node* novoNo = criarNo(matricula, nome, NULL);
    if (!raiz) {
        novoNo->cor = PRETO;
        return novoNo;
    }
    Node* atual = raiz;
    Node* pai = NULL;
    while (atual) {
        pai = atual;
        if (matricula < atual->matricula)
            atual = atual->esquerda;
        else
            atual = atual->direita;
    }
    novoNo->pai = pai;
    if (matricula < pai->matricula)
        pai->esquerda = novoNo;
    else
        pai->direita = novoNo;
    return balancearInsercao(raiz, novoNo);
}

// Busca um nó na árvore
Node* buscar(Node* raiz, int matricula) {
    while (raiz && raiz->matricula != matricula) {
        if (matricula < raiz->matricula)
            raiz = raiz->esquerda;
        else
            raiz = raiz->direita;
    }
    return raiz;
}

// Função para remover um nó corretamente
Node* remover(Node* raiz, int matricula) {
    Node* no = buscar(raiz, matricula);
    if (!no) return raiz;
    if (no->esquerda && no->direita) {
        Node* substituto = no->direita;
        while (substituto->esquerda) substituto = substituto->esquerda;
        no->matricula = substituto->matricula;
        strcpy(no->nome, substituto->nome);
        no = substituto;
    }
    Node* filho = (no->esquerda) ? no->esquerda : no->direita;
    if (filho) filho->pai = no->pai;
    if (!no->pai) raiz = filho;
    else if (no == no->pai->esquerda) no->pai->esquerda = filho;
    else no->pai->direita = filho;
    free(no);
    return raiz;
}

// Impressão da árvore
void imprimirArvore(Node* raiz, int nivel) {
    if (raiz == NULL) return;
    imprimirArvore(raiz->direita, nivel + 1);
    for (int i = 0; i < nivel; i++) printf("    ");
    printf("%d (%s)\n", raiz->matricula, raiz->cor == VERMELHO ? "R" : "B");
    imprimirArvore(raiz->esquerda, nivel + 1);
}

// Função principal
int main() {
    Node* raiz = NULL;
    int opcao, matricula;
    char nome[100];
    do {
        printf("|----------MENU----------|\n");
        printf("|   1 - Inserir aluno    |\n");
        printf("|   2 - Buscar aluno     |\n");
        printf("|   3 - Imprimir árvore  |\n");
        printf("|   4 - Remover aluno    |\n");
        printf("|   5 - Sair             |\n");
        printf("|------------------------|\n");
        scanf("%d", &opcao);
        getchar();
        switch (opcao) {
            case 1:
                printf("Digite a matrícula: ");
                scanf("%d", &matricula);
                getchar();
                printf("Digite o nome: ");
                fgets(nome, 100, stdin);
                strtok(nome, "\n");
                raiz = inserir(raiz, matricula, nome);
                break;
            case 2:
                printf("Digite a matrícula: ");
                scanf("%d", &matricula);
                Node* aluno = buscar(raiz, matricula);
                if (aluno) printf("Aluno encontrado: %s\n", aluno->nome);
                else printf("Aluno não encontrado.\n");
                break;
            case 3:
                printf("\nÁrvore Rubro-Negra:\n");
                imprimirArvore(raiz, 0);
                break;
            case 4:
                printf("Digite a matrícula a remover: ");
                scanf("%d", &matricula);
                raiz = remover(raiz, matricula);
                break;
            case 5:
                printf("Saindo...\n");
                break;
            default:
                printf("Opção inválida!\n");
        }
    } while (opcao != 5);
    return 0;
}
