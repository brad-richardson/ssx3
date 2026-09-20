#include <stdio.h>
#include <SDL2/SDL.h>
int main(int argc, char *argv[]) {
    printf("PROBE: SDL_main entered argc=%d argv1=%s\n", argc, argc > 1 ? argv[1] : "(none)");
    fflush(stdout);
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("PROBE: SDL_Init failed: %s\n", SDL_GetError());
        fflush(stdout);
        return 1;
    }
    printf("PROBE: SDL_Init OK video=%s\n", SDL_GetCurrentVideoDriver());
    fflush(stdout);
    SDL_Window *w = SDL_CreateWindow("probe", 0, 0, 200, 200, SDL_WINDOW_SHOWN);
    printf("PROBE: window=%p err=%s\n", (void *)w, SDL_GetError());
    fflush(stdout);
    SDL_Delay(1500);
    if (w) SDL_DestroyWindow(w);
    SDL_Quit();
    printf("PROBE: clean exit\n");
    fflush(stdout);
    return 0;
}
