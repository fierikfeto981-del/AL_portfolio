#include <SFML/Graphics.hpp>
#include <sstream>
#include <algorithm>

#include "GameConfig.h"
#include "Snake.h"
#include "Food.h"
#include "SpecialFood.h"

using namespace GameConfig;

void drawGrid(sf::RenderWindow& window) {

    sf::RectangleShape line;

    line.setFillColor(COL_GRID);

    for (int x = 0; x <= GRID_W; x++) {

        line.setSize(sf::Vector2f(
            1.f,
            GRID_H * CELL_SIZE
        ));

        line.setPosition(x * CELL_SIZE, 0);

        window.draw(line);
    }

    for (int y = 0; y <= GRID_H; y++) {

        line.setSize(sf::Vector2f(
            GRID_W * CELL_SIZE,
            1.f
        ));

        line.setPosition(0, y * CELL_SIZE);

        window.draw(line);
    }
}

int main() {

    sf::RenderWindow window(
        sf::VideoMode(WINDOW_W, WINDOW_H),
        "Snake Game - SFML 2.5.1"
    );

    window.setFramerateLimit(60);

    sf::Font font;

    if (!font.loadFromFile("arial.ttf"))
        return -1;

    sf::Text hudText;

    hudText.setFont(font);
    hudText.setCharacterSize(18);
    hudText.setFillColor(COL_TEXT);

    hudText.setPosition(
        5,
        GRID_H * CELL_SIZE + 8
    );

    Snake snake;

    Food food(snake);

    SpecialFood specialFood(snake);

    int score = 0;

    int highScore = 0;

    bool gameOver = false;

    bool paused = false;

    float moveTimer = 0.f;

    sf::Clock clock;

    while (window.isOpen()) {

        float dt = clock.restart().asSeconds();

        sf::Event event;

        while (window.pollEvent(event)) {

            if (event.type == sf::Event::Closed) {
                window.close();
            }

            if (event.type == sf::Event::KeyPressed) {

                if (!gameOver) {

                    if (event.key.code == sf::Keyboard::Up)
                        snake.setDirection(Direction::UP);

                    else if (event.key.code == sf::Keyboard::Down)
                        snake.setDirection(Direction::DOWN);

                    else if (event.key.code == sf::Keyboard::Left)
                        snake.setDirection(Direction::LEFT);

                    else if (event.key.code == sf::Keyboard::Right)
                        snake.setDirection(Direction::RIGHT);

                    else if (event.key.code == sf::Keyboard::P)
                        paused = !paused;
                }

                if (gameOver &&
                    event.key.code == sf::Keyboard::R) {

                    snake = Snake();

                    food = Food(snake);

                    specialFood = SpecialFood(snake);

                    score = 0;

                    gameOver = false;

                    moveTimer = 0.f;
                }
            }
        }

        if (!gameOver && !paused) {

            moveTimer += dt;

            specialFood.update(dt);

            float speedBoost =
                (score / 5) * 0.01f;

            float currentInterval =
                std::max(
                    0.05f,
                    MOVE_INTERVAL - speedBoost
                );

            if (moveTimer >= currentInterval) {

                moveTimer = 0.f;

                if (!snake.move()) {

                    gameOver = true;

                    if (score > highScore)
                        highScore = score;
                }

                else if (
                    snake.getHead()
                    == food.getPosition()
                ) {

                    snake.grow();

                    score += food.getPoints();

                    food.respawn(snake);

                    if (score > 0 &&
                        score % 10 == 0 &&
                        !specialFood.isActive()) {

                        specialFood.activate(snake);
                    }
                }

                if (
                    specialFood.isActive() &&
                    snake.getHead()
                    == specialFood.getPosition()
                ) {

                    snake.grow();

                    score += specialFood.getPoints();

                    specialFood.deactivate();
                }
            }
        }

        window.clear(COL_BG);

        drawGrid(window);

        food.draw(window);

        specialFood.draw(window);

        snake.draw(window);

        std::ostringstream oss;

        if (gameOver) {

            oss << "GAME OVER! Skor: "
                << score
                << "  High Score: "
                << highScore
                << "  [R] Restart";
        }

        else if (paused) {

            oss << "PAUSED [P] Continue";
        }

        else {

            oss << "Skor: "
                << score
                << "  High Score: "
                << highScore
                << "  Panjang: "
                << snake.getLength()
                << "  [P] Pause";
        }

        hudText.setString(oss.str());

        window.draw(hudText);

        if (gameOver) {

            sf::RectangleShape overlay;

            overlay.setSize(
                sf::Vector2f(
                    WINDOW_W,
                    WINDOW_H
                )
            );

            overlay.setFillColor(
                sf::Color(0, 0, 0, 150)
            );

            window.draw(overlay);

            sf::Text goText;

            goText.setFont(font);

            goText.setString("GAME OVER");

            goText.setCharacterSize(36);

            goText.setFillColor(sf::Color::Red);

            sf::FloatRect bounds =
                goText.getLocalBounds();

            goText.setOrigin(
                bounds.width / 2.f,
                bounds.height / 2.f
            );

            goText.setPosition(
                WINDOW_W / 2.f,
                WINDOW_H / 2.f - 30.f
            );

            window.draw(goText);
        }

        window.display();
    }

    return 0;
}