#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Estrutura do nó da árvore
typedef struct Node {
    int isbn;
    char titulo[100];
    char autor[100];
    int ano;
    struct Node *esquerda;
    struct Node *direita;
} Node;

// Função para criar um novo nó
Node* criarNo(int isbn, char titulo[], char autor[], int ano) {
    Node* novoNo = (Node*)malloc(sizeof(Node));
    novoNo->isbn = isbn;
    strcpy(novoNo->titulo, titulo);
    strcpy(novoNo->autor, autor);
    novoNo->ano = ano;
    novoNo->esquerda = NULL;
    novoNo->direita = NULL;
    return novoNo;
}

// Função para inserir um nó na árvore
Node* inserir(Node* raiz, int isbn, char titulo[], char autor[], int ano) {
    if (raiz == NULL) {
        return criarNo(isbn, titulo, autor, ano);
    }
    if (isbn < raiz->isbn) {
        raiz->esquerda = inserir(raiz->esquerda, isbn, titulo, autor, ano);
    } else if (isbn > raiz->isbn) {
        raiz->direita = inserir(raiz->direita, isbn, titulo, autor, ano);
    }
    return raiz;
}

// Função para encontrar o nó com menor valor (usado na remoção)
Node* encontrarMinimo(Node* raiz) {
    while (raiz->esquerda != NULL) {
        raiz = raiz->esquerda;
    }
    return raiz;
}

// Função para remover um nó
Node* remover(Node* raiz, int isbn) {
    if (raiz == NULL) return raiz;
    
    if (isbn < raiz->isbn) {
        raiz->esquerda = remover(raiz->esquerda, isbn);
    } else if (isbn > raiz->isbn) {
        raiz->direita = remover(raiz->direita, isbn);
    } else {
        if (raiz->esquerda == NULL) {
            Node* temp = raiz->direita;
            free(raiz);
            return temp;
        } else if (raiz->direita == NULL) {
            Node* temp = raiz->esquerda;
            free(raiz);
            return temp;
        }
        Node* temp = encontrarMinimo(raiz->direita);
        raiz->isbn = temp->isbn;
        strcpy(raiz->titulo, temp->titulo);
        strcpy(raiz->autor, temp->autor);
        raiz->ano = temp->ano;
        raiz->direita = remover(raiz->direita, temp->isbn);
    }
    return raiz;
}

// Percursos
void preOrdem(Node* raiz) {
    if (raiz != NULL) {
        printf("%02d - %s\n", raiz->isbn, raiz->titulo);
        preOrdem(raiz->esquerda);
        preOrdem(raiz->direita);
    }
}
void emOrdem(Node* raiz) {
    if (raiz != NULL) {
        emOrdem(raiz->esquerda);
        printf("%02d - %s\n", raiz->isbn, raiz->titulo);
        emOrdem(raiz->direita);
    }
}
void posOrdem(Node* raiz) {
    if (raiz != NULL) {
        posOrdem(raiz->esquerda);
        posOrdem(raiz->direita);
        printf("%02d - %s\n", raiz->isbn, raiz->titulo);
    }
}

// Função para imprimir a árvore
void imprimirArvore(Node* raiz, int espacos) {
    if (raiz == NULL) return;
    imprimirArvore(raiz->direita, espacos + 4);
    for (int i = 0; i < espacos; i++) printf(" ");
    printf("%02d\n", raiz->isbn);
    imprimirArvore(raiz->esquerda, espacos + 4);
}

// Função principal
int main() {
    Node* raiz = NULL;
    int opcao;
    
    do {
        printf("\n-------------------------------------------\n");
        printf("|                 MENU                    |\n");
        printf("| 1 - Inserir livro                       |\n");
        printf("| 2 - Remover livro                       |\n");
        printf("| 3 - Imprimir árvore                     |\n");
        printf("| 4 - Imprimir percurso em pré-ordem      |\n");
        printf("| 5 - Imprimir percurso em ordem          |\n");
        printf("| 6 - Imprimir percurso em pós-ordem      |\n");
        printf("| 7 - Sair                                |\n");
        printf("| ESCOLHA UMA OPCAO                       |\n");
        printf("------------------------------------------\n");
        scanf("%d", &opcao);
        getchar(); // Limpa buffer
        
        if (opcao == 1) {
            char titulo[100], autor[100];
            int isbn, ano;
            printf("Digite o ISBN: "); scanf("%d", &isbn);
            getchar();
            printf("Digite o título: "); fgets(titulo, 100, stdin); strtok(titulo, "\n");
            printf("Digite o autor: "); fgets(autor, 100, stdin); strtok(autor, "\n");
            printf("Digite o ano: "); scanf("%d", &ano);
            raiz = inserir(raiz, isbn, titulo, autor, ano);
        } 
        else if (opcao == 2) {
            int isbn;
            printf("Digite o ISBN do livro a remover: ");
            scanf("%d", &isbn);
            raiz = remover(raiz, isbn);
        }
        else if (opcao == 3) {
            printf("\nÁrvore após inserção:\n");
            imprimirArvore(raiz, 0);
        }
        else if (opcao == 4) {
            printf("\nPré-Ordem:\n");
            preOrdem(raiz);
        }
        else if (opcao == 5) {
            printf("\nEm Ordem:\n");
            emOrdem(raiz);
        }
        else if (opcao == 6) {
            printf("\nPós-Ordem:\n");
            posOrdem(raiz);
        }
        else if (opcao == 7) {
            printf("Saindo...\n");
        } 
        else {
            printf("Opção inválida!\n");
        }
    } while (opcao != 7);
    return 0;
}
