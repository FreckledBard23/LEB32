#undef main
#define SDL_MAIN_HANDLED
#include <SDL.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#define PI 3.1415926535


#define screenx 256
#define screeny 256

Uint32 pixels[screenx * screeny];

void setPixel(Uint32 color, int x, int y){
    pixels[y * screenx + x] = color;
}

void clear_screen(Uint32 color){
    for(int i = 0; i < screeny * screenx; ++i){pixels[i] = color;}
}

//takes in ul x and y and x and y side lengths to draw a filled rectangle
void draw_box_filled(int x, int y, Uint32 color, int xside, int yside){
    for(int xoff = 0; xoff < xside; ++xoff){
        for(int yoff = 0; yoff < yside; ++yoff){ 
            int newx = x + xoff;
            int newy = y + yoff;
            if(newx < screenx && newx >= 0 && newy < screeny && newy >= 0)
                pixels[newy * screenx + newx] = color;
        }
    }
}

bool ascii_table[8128];
char keyboard_buffer = (char)(0);
//takes in ul x and y and x and y side lengths to draw a char
void draw_char(int x, int y, Uint32 color, int xside, int yside, char character){
    for(int xoff = 0; xoff < xside; ++xoff){
        for(int yoff = 0; yoff < yside; ++yoff){ 
            int newx = x + xoff;
            int newy = y + yoff;

            bool draw = ascii_table[character * 64 + (yoff * xside + xoff)];

            if(newx < screenx && newx >= 0 && newy < screeny && newy >= 0 && draw){
                pixels[newy * screenx + newx] = color;
            }
        }
    }
}



#define num_regs 16
#define memory_block_size 16777216
int regs[16];
int ram[memory_block_size];
int rom[memory_block_size];
int screen[memory_block_size];
unsigned int addr = 0;

int stack[256];
int stack_pointer = 0;

long long int unsigned_max = 4294967296;
void overflow_check_addr(){
    if(addr > unsigned_max){
        addr -= unsigned_max;
    }
}

#define MAX_LINE_LENGTH 1024
#define NUM_ROWS 2097152 // Adjust this based on the maximum address in your file

int read_rom(char* file_name){
    char progress_bar[19];
    int last_whole_percentage = 0;

    for(int i = 0; i < 20; i++){
        progress_bar[i] = ' ';
    }

    FILE *file;
    char line[MAX_LINE_LENGTH];

    file = fopen(file_name, "r"); // Replace "hex_values.txt" with your file name

    if (file == NULL) {
        perror("Error opening file for ROM");
        return 1;
    }

    for (int i = 0; i < NUM_ROWS; i++) {
        if (fgets(line, MAX_LINE_LENGTH, file) == NULL) {
            break; // End of file or an error occurred
        }

        // Skip the address at the side and read hex values
        sscanf(line, "%*x: %x %x %x %x %x %x %x %x",
               &rom[i * 8 + 0], &rom[i * 8 + 1], &rom[i * 8 + 2], &rom[i * 8 + 3],
               &rom[i * 8 + 4], &rom[i * 8 + 5], &rom[i * 8 + 6], &rom[i * 8 + 7]);

        float percent_done = ((float)i / NUM_ROWS) * 20;

        for(int character = 0; character < 20; character++){
            if(character <= percent_done){
                progress_bar[character] = '=';
            } else {
                progress_bar[character] = ' ';
            }
        }

        if((int)percent_done > last_whole_percentage){
            for(int i = 0; i < 27; i++){
                printf("\b"); //hacky way to clear progress bar
            }
            printf("     [%s]", progress_bar);
            last_whole_percentage = (int)percent_done;
        }
    }

    printf(" DONE!\n"); //needed newline after progress bar;
    fclose(file);
}

int read_ascii(){
    const int num_of_lines = 256;

    FILE *file;
    char line[MAX_LINE_LENGTH];

    file = fopen("ascii_table", "r"); // Replace "hex_values.txt" with your file name

    if (file == NULL) {
        perror("Error opening file for ASCII");
        return 1;
    }

    for (int i = 0; i < num_of_lines; i++) {
        if (fgets(line, MAX_LINE_LENGTH, file) == NULL) {
            break; // End of file or an error occurred
        }

        // Skip the address at the side and read hex values
        sscanf(line, "%*x: %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x",
               &ascii_table[i * 32 + 0], &ascii_table[i * 32 + 1], &ascii_table[i * 32 + 2], &ascii_table[i * 32 + 3],
               &ascii_table[i * 32 + 4], &ascii_table[i * 32 + 5], &ascii_table[i * 32 + 6], &ascii_table[i * 32 + 7],
               &ascii_table[i * 32 + 8], &ascii_table[i * 32 + 9], &ascii_table[i * 32 +10], &ascii_table[i * 32 +11],
               &ascii_table[i * 32 +12], &ascii_table[i * 32 +13], &ascii_table[i * 32 +14], &ascii_table[i * 32 +15],
               &ascii_table[i * 32 +16], &ascii_table[i * 32 +17], &ascii_table[i * 32 +18], &ascii_table[i * 32 +19],
               &ascii_table[i * 32 +20], &ascii_table[i * 32 +21], &ascii_table[i * 32 +22], &ascii_table[i * 32 +23],
               &ascii_table[i * 32 +24], &ascii_table[i * 32 +25], &ascii_table[i * 32 +26], &ascii_table[i * 32 +27],
               &ascii_table[i * 32 +28], &ascii_table[i * 32 +29], &ascii_table[i * 32 +30], &ascii_table[i * 32 +31]);
    }

    printf("\n                            DONE!\n");
    fclose(file);
}

int mem(int address){
    int block = address / memory_block_size;

    if(address == 0xffffffff){
        int return_value = (int)keyboard_buffer;
        keyboard_buffer = (char)(0);
        return return_value;
    }

    switch (block)
    {
        case 0:
            return rom[address];
            break;
        case 1:
            return ram[address - memory_block_size];
            break;
        
        default:
            break;
    }

    return 0;
}

int get_mem_block(int address){
    return address / memory_block_size;
}

int main(int argc, char *argv[]){
    if(argc < 2){
        printf("Add a filename for ROM!\nTry calling ./emulator.exe {ROM filename}\n");
        return 1;
    }

    bool debugging = false;
    if(argc >= 3){
        if(!strcmp(argv[2], "-d")){
            printf("Debugging Enabled\n");
            debugging = true;
        }
    }

    printf("Reading File for ROM: %s\n", argv[1]);

    read_rom(argv[1]);

    printf("Reading ASCII table");

    read_ascii();

    printf("Starting Emulator\n");



    SDL_Init(SDL_INIT_VIDEO);

    SDL_Window* window = SDL_CreateWindow("LEB32 Emulator", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, screenx, screeny, SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, 0);
    SDL_Texture* texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STATIC, screenx, screeny);

    bool quit = false;

    SDL_Event event;

    clear_screen(0x0);



    bool halted = false;
    while (!halted)
    {   
        //---------SDL---------//
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                halted = true;
            }

            if (event.type == SDL_TEXTINPUT) {
                // Handle text input events
                keyboard_buffer = event.text.text[0];
            }
        }

        // Update the texture with the pixel data
        SDL_UpdateTexture(texture, NULL, pixels, screenx * sizeof(Uint32));

        // Clear the renderer
        SDL_RenderClear(renderer);

        // Render the texture
        SDL_RenderCopy(renderer, texture, NULL, NULL);




        int entire_instruction = mem(addr);
        int inst = entire_instruction & 0xF;
        int R2 = (entire_instruction & 0xF0) >> 4;
        int R1 = (entire_instruction & 0xF00) >> 8;
        int W1 = (entire_instruction & 0xF000) >> 12;
        int inst_data = (entire_instruction & 0xFFFF0000) >> 16;

        if(debugging){
            printf("addr: %08x inst: %04x, %x, %x, %x, %x\n", 
                          addr, inst_data, W1, R1, R2, inst);
        }
        
        //hlt
        if(inst == 1){
            halted = true;
        }

        //str
        if(inst == 2){
            regs[W1] = inst_data;
        }

        //mst
        if(inst == 3){
            regs[W1] = mem(regs[R2] + (memory_block_size * inst_data));
        }

        //alu
        if(inst == 4){
            switch (inst_data)
            {
                case 0:
                    regs[W1] = regs[R1] + regs[R2];
                    break;
                case 1:
                    regs[W1] = regs[R1] - regs[R2];
                    break;
                case 2:
                    regs[W1] = regs[R1] * regs[R2];
                    break;
                case 3:
                    regs[W1] = regs[R1] / regs[R2];
                    break;
                case 4:
                    regs[W1] = regs[R1] << regs[R2];
                    break;
                case 5:
                    regs[W1] = regs[R1] >> regs[R2];
                    break;
            
                default:
                    regs[W1] = regs[R1] + regs[R2];
                    break;
            }
        }

        //jmp
        bool jmp = false;
        if(inst == 5){
            int condition = inst_data & 0xF;
            int jump_register_addr = (inst_data & 0xF0) >> 4;

            switch (condition)
            {
                case 0:
                    addr = regs[jump_register_addr];
                    jmp = true;
                    break;
                case 1:
                    if(regs[R1] == regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                case 2:
                    if(regs[R1] != regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                case 3:
                    if(regs[R1] > regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                case 4:
                    if(regs[R1] < regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                case 5:
                    if(regs[R1] >= regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                case 6:
                    if(regs[R1] <= regs[R2]){
                        addr = regs[jump_register_addr];
                        jmp = true;
                    }
                    break;
                
                default:
                    break;
            }
        }

        //wrt
        if(inst == 6){
            switch (get_mem_block(regs[R2] + inst_data * memory_block_size))
            {
                case 1:
                    ram[regs[R2]] = regs[R1];
                    break;
                case 2:
                    if(regs[R2] < screenx * screeny){
                        if((inst_data >> 7) == 1){
                            pixels[regs[R2]] = regs[R1];
                        } else {
                            int y = regs[R2] / screenx;
                            int x = regs[R2] % screenx;

                            draw_char(x, y, regs[R1], 8, 8, (char)(regs[R1] >> 24));
                        }
                    }
                
                default:
                    break;
            }
        }
        
        //push
        if(inst == 7){
            stack[stack_pointer] = regs[R1];
            stack_pointer++;

            if(stack_pointer > 255){
                stack_pointer = 0;
            }
        }

        //pop
        if(inst == 8){
            regs[W1] = stack[stack_pointer];
            stack_pointer--;

            if(stack_pointer < 0){
                stack_pointer = 255;
            }
        }

        if(!jmp){
            addr++;
        }

        printf("%x %x %x\n", regs[0], regs[1], regs[4]);
        // Update the screen
        SDL_RenderPresent(renderer);
    }

    SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}