def run():
    try:
        import pygame
    except ImportError:
        print("Install pygame for this case study: pip install pygame")
        return
    pygame.init()
    screen = pygame.display.set_mode((700, 400))
    pygame.display.set_caption("TripSplit Pygame Case Study")
    clock = pygame.time.Clock()
    running = True
    x = 50
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        x += 2
        if x > 650:
            x = 50
        screen.fill((245, 245, 245))
        pygame.draw.circle(screen, (60, 60, 60), (x, 200), 25)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    run()
