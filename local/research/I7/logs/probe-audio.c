#include <stdio.h>
#include <SDL2/SDL.h>
int main(int argc, char *argv[]) {
    printf("APROBE: SDL_main entered\n"); fflush(stdout);
    if (SDL_Init(SDL_INIT_AUDIO) != 0) {
        printf("APROBE: SDL_Init AUDIO failed: %s\n", SDL_GetError()); fflush(stdout);
        return 1;
    }
    printf("APROBE: SDL_Init AUDIO ok driver=%s\n", SDL_GetCurrentAudioDriver());
    fflush(stdout);
    SDL_AudioSpec want, have;
    SDL_zero(want);
    want.freq = 48000; want.format = AUDIO_S16SYS; want.channels = 2; want.samples = 1024;
    SDL_AudioDeviceID dev = SDL_OpenAudioDevice(NULL, 0, &want, &have, 0);
    printf("APROBE: device=%u err=%s have=%dHz ch=%d\n", (unsigned)dev, SDL_GetError(), have.freq, have.channels);
    fflush(stdout);
    SDL_Delay(1000);
    if (dev) SDL_CloseAudioDevice(dev);
    SDL_Quit();
    printf("APROBE: clean exit\n"); fflush(stdout);
    return 0;
}
