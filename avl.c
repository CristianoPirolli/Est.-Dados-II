#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Estrutura do nó da árvore AVL
typedef struct Node {
    int matricula;
    char nome[100];
    int altura;
    struct Node *esquerda;
    struct Node *direita;
} Node;

// Função para obter a altura de um nó
int altura(Node *n) {
    return n ? n->altura : 0;
}

// Função para obter o fator de balanceamento
int fatorBalanceamento(Node *n) {
    return n ? altura(n->esquerda) - altura(n->direita) : 0;
}

// Função para criar um novo nó
Node* criarNo(int matricula, char nome[]) {
    Node* novoNo = (Node*)malloc(sizeof(Node));
    novoNo->matricula = matricula;
    strcpy(novoNo->nome, nome);
    novoNo->altura = 1;
    novoNo->esquerda = NULL;
    novoNo->direita = NULL;
    return novoNo;
}

// Função para realizar rotação à direita
Node* rotacaoDireita(Node *y) {
    Node *x = y->esquerda;
    Node *T2 = x->direita;
    
    x->direita = y;
    y->esquerda = T2;
    
    y->altura = 1 + (altura(y->esquerda) > altura(y->direita) ? altura(y->esquerda) : altura(y->direita));
    x->altura = 1 + (altura(x->esquerda) > altura(x->direita) ? altura(x->esquerda) : altura(x->direita));
    
    return x;
}

// Função para realizar rotação à esquerda
Node* rotacaoEsquerda(Node *x) {
    Node *y = x->direita;
    Node *T2 = y->esquerda;
    
    y->esquerda = x;
    x->direita = T2;
    
    x->altura = 1 + (altura(x->esquerda) > altura(x->direita) ? altura(x->esquerda) : altura(x->direita));
    y->altura = 1 + (altura(y->esquerda) > altura(y->direita) ? altura(y->esquerda) : altura(y->direita));
    
    return y;
}

// Função para balancear um nó
Node* balancear(Node *raiz) {
    int fb = fatorBalanceamento(raiz);
    
    if (fb > 1 && fatorBalanceamento(raiz->esquerda) >= 0)
        return rotacaoDireita(raiz);
    
    if (fb < -1 && fatorBalanceamento(raiz->direita) <= 0)
        return rotacaoEsquerda(raiz);
    
    if (fb > 1 && fatorBalanceamento(raiz->esquerda) < 0) {
        raiz->esquerda = rotacaoEsquerda(raiz->esquerda);
        return rotacaoDireita(raiz);
    }
    
    if (fb < -1 && fatorBalanceamento(raiz->direita) > 0) {
        raiz->direita = rotacaoDireita(raiz->direita);
        return rotacaoEsquerda(raiz);
    }
    
    return raiz;
}

// Função para encontrar o menor nó (usado na remoção)
Node* encontrarMinimo(Node* raiz) {
    while (raiz->esquerda != NULL)
        raiz = raiz->esquerda;
    return raiz;
}

// Função para inserir um nó na árvore AVL
Node* inserir(Node* raiz, int matricula, char nome[]) {
    if (raiz == NULL) return criarNo(matricula, nome);
    
    if (matricula < raiz->matricula)
        raiz->esquerda = inserir(raiz->esquerda, matricula, nome);
    else if (matricula > raiz->matricula)
        raiz->direita = inserir(raiz->direita, matricula, nome);
    else
        return raiz;
    
    raiz->altura = 1 + (altura(raiz->esquerda) > altura(raiz->direita) ? altura(raiz->esquerda) : altura(raiz->direita));
    return balancear(raiz);
}

// Função para remover um nó da árvore AVL
Node* remover(Node* raiz, int matricula) {
    if (raiz == NULL) return raiz;
    
    if (matricula < raiz->matricula)
        raiz->esquerda = remover(raiz->esquerda, matricula);
    else if (matricula > raiz->matricula)
        raiz->direita = remover(raiz->direita, matricula);
    else {
        if (raiz->esquerda == NULL || raiz->direita == NULL) {
            Node *temp = raiz->esquerda ? raiz->esquerda : raiz->direita;
            free(raiz);
            return temp;
        }
        Node *temp = encontrarMinimo(raiz->direita);
        raiz->matricula = temp->matricula;
        strcpy(raiz->nome, temp->nome);
        raiz->direita = remover(raiz->direita, temp->matricula);
    }
    
    raiz->altura = 1 + (altura(raiz->esquerda) > altura(raiz->direita) ? altura(raiz->esquerda) : altura(raiz->direita));
    return balancear(raiz);
}

// Função para buscar um aluno por matrícula
Node* buscar(Node* raiz, int matricula) {
    if (raiz == NULL || raiz->matricula == matricula)
        return raiz;
    if (matricula < raiz->matricula)
        return buscar(raiz->esquerda, matricula);
    return buscar(raiz->direita, matricula);
}

// Função para imprimir a árvore visualmente na vertical
void imprimirArvore(Node* raiz, int nivel) {
    if (raiz == NULL) return;
    
    imprimirArvore(raiz->direita, nivel + 1);
    
    for (int i = 0; i < nivel; i++) printf("    ");
    printf("%d\n", raiz->matricula);
    
    imprimirArvore(raiz->esquerda, nivel + 1);
}

// Função principal
int main() {
    Node* raiz = NULL;
    int opcao, matricula;
    char nome[100];
    
    do {
        printf("\n-------------------------------------------\n");
        printf("|                  MENU                   |\n");
        printf("|                                         |\n");
        printf("|  1 - Inserir aluno                      |\n");
        printf("|  2 - Remover aluno                      |\n");
        printf("|  3 - Buscar aluno                       |\n");
        printf("|  4 - Imprimir árvore                    |\n");
        printf("|  5 - Sair                               |\n");
        printf("|                                         |\n");
        printf("-------------------------------------------\n");
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
                printf("Digite a matrícula a remover: ");
                scanf("%d", &matricula);
                raiz = remover(raiz, matricula);
                break;
            case 3:
                printf("Digite a matrícula: ");
                scanf("%d", &matricula);
                Node* aluno = buscar(raiz, matricula);
                if (aluno) printf("Aluno encontrado: %s\n", aluno->nome);
                else printf("Aluno não encontrado.\n");
                break;
            case 4:
                printf("\nÁrvore AVL:\n");
                imprimirArvore(raiz, 0);
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
