#include <stdio.h>
#define MAX 10

int main() {
    int n, m; // n = number of processes, m = number of resources
    int alloc[MAX][MAX], max[MAX][MAX], need[MAX][MAX];
    int avail[MAX];
    int finish[MAX] = {0};
    int safeSeq[MAX];
    int i, j, k, count = 0;

    printf("Enter number of processes: ");
    scanf("%d", &n);

    printf("Enter number of resource types: ");
    scanf("%d", &m);

    // Allocation Matrix
    printf("Enter Allocation Matrix:\n");
    for(i = 0; i < n; i++) {
        for(j = 0; j < m; j++) {
            scanf("%d", &alloc[i][j]);
        }
    }

    // Max Matrix
    printf("Enter Max Matrix:\n");
    for(i = 0; i < n; i++) {
        for(j = 0; j < m; j++) {
            scanf("%d", &max[i][j]);
        }
    }

    // Available Resources
    printf("Enter Available Resources:\n");
    for(i = 0; i < m; i++) {
        scanf("%d", &avail[i]);
    }

    // Calculate Need Matrix
    for(i = 0; i < n; i++) {
        for(j = 0; j < m; j++) {
            need[i][j] = max[i][j] - alloc[i][j];
        }
    }

    // Banker's Algorithm
    while(count < n) {
        int found = 0;

        for(i = 0; i < n; i++) {
            if(finish[i] == 0) {
                int flag = 0;

                // Check if need <= avail
                for(j = 0; j < m; j++) {
                    if(need[i][j] > avail[j]) {
                        flag = 1;
                        break;
                    }
                }

                if(flag == 0) {
                    // Add allocated resources to available
                    for(k = 0; k < m; k++) {
                        avail[k] += alloc[i][k];
                    }

                    safeSeq[count++] = i;
                    finish[i] = 1;
                    found = 1;
                }
            }
        }

        if(found == 0) {
            printf("\nSystem is NOT in a safe state (Deadlock possible)\n");
            return 0;
        }
    }
    printf("\nSystem is in a SAFE state.\nSafe sequence:\n");
    for(i = 0; i < n; i++) {
        printf("P%d", safeSeq[i]);
        if(i != n - 1)
            printf(" -> ");
    }

    printf("\n");
    return 0;
}