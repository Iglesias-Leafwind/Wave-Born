import pygame


def load_images(spritesheet, sprite_width, sprite_height, scale, positions):
    return [pygame.transform.scale(
        spritesheet.image_at(
            (a * sprite_width, b * sprite_height, sprite_width, sprite_height), -1
        ).convert_alpha(),
        scale,
    )
        for a, b in positions
    ]


def invert_images(images):
    return [pygame.transform.flip(mi, True, False) for mi in images]