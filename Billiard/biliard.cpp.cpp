#include <SFML/Graphics.hpp>
#include <cmath>
#include <vector>
#include <string>

struct Ball {
    sf::CircleShape shape;
    int number;
    sf::Color color;
};

int main() {
    sf::RenderWindow window(sf::VideoMode(1280, 720), "Billiard PRO");

    
    sf::RectangleShape tableBorder(sf::Vector2f(1000.5f, 550.f));
    tableBorder.setFillColor(sf::Color(100, 50, 0)); 
    tableBorder.setPosition(140.f, 85.f);

    sf::RectangleShape tableCloth(sf::Vector2f(960.f, 510.f));
    tableCloth.setFillColor(sf::Color(0, 100, 0)); 
    tableCloth.setPosition(160.f, 105.f);
};

    float pocketRadius = 22.f;
    std::vector<sf::Vector2f> pockets = {
        {160.f, 105.f},
        {640.f, 105.f}, 
        {1120.f, 105.f},
        {160.f, 615.f}, 
        {640.f, 615.f}, 
        {1120.f, 615.f} 
    };

    sf::RectangleShape centerLine(sf::Vector2f(4.f, 510.f));
    centerLine.setFillColor(sf::Color::White);
    centerLine.setPosition(638.f, 105.f);

    sf::CircleShape centerPoint(4.f);
    centerPoint.setFillColor(sf::Color::White);
    centerPoint.setOrigin(4.f, 4.f);
    centerPoint.setPosition(640.f, 360.f);

    float ballRadius = 14.f;
    
    sf::Color cYellow(255, 204, 0);
    sf::Color cBlue(0, 51, 153);
    sf::Color cRed(204, 0, 0);
    sf::Color cPurple(102, 0, 102);
    sf::Color cOrange(255, 102, 0);
    sf::Color cGreen(0, 102, 0);
    sf::Color cMaroon(102, 0, 0);
    sf::Color cBlack(30, 30, 30);
    sf::Color cPink(255, 182, 193);

    Ball cueBall;
    cueBall.number = 0;
    cueBall.color = sf::Color::White;
    cueBall.shape.setRadius(ballRadius);
    cueBall.shape.setOrigin(ballRadius, ballRadius);
    cueBall.shape.setFillColor(cueBall.color);
    cueBall.shape.setPosition(350.f, 360.f);

    struct BallData { int num; sf::Color col; sf::Vector2f pos; };
    float startX = 850.f;
    float startY = 360.f;
    float gap = 28.5f; 

    std::vector<BallData> ballList = {

        {1, cYellow, {startX, startY}},
        {2, cBlue,   {startX + gap, startY - gap / 2.f}},
        {4, cOrange, {startX + gap, startY + gap / 2.f}},
        {3, cRed,    {startX + gap * 2, startY - gap}},
        {5, cPurple, {startX + gap * 2, startY}},
        {8, cPink,   {startX + gap * 2, startY + gap}},
        {6, cGreen,  {startX + gap * 3, startY - gap * 1.5f}},
        {7, cMaroon, {startX + gap * 3, startY - gap * 0.5f}},
        {9, cBlack,  {startX + gap * 3, startY + gap * 0.5f}}

    std::vector<Ball> rackBalls;
    for (auto& bd : ballList) {
        Ball b;
        b.number = bd.num;
        b.color = bd.col;
        b.shape.setRadius(ballRadius);
        b.shape.setOrigin(ballRadius, ballRadius);
        b.shape.setFillColor(b.color);
        b.shape.setOutlineThickness(1.5f);
        b.shape.setOutlineColor(sf::Color::Black);
        b.shape.setPosition(bd.pos);
        rackBalls.push_back(b);
    }

    sf::Font font;
    bool hasFont = font.loadFromFile("arial.ttf"); 

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
        }

        window.clear(sf::Color(15, 15, 15)); 

        window.draw(tableBorder);
        window.draw(tableCloth);
        window.draw(centerLine);
        window.draw(centerPoint);

        for (auto& pPos : pockets) {
            sf::CircleShape pocket(pocketRadius);
            pocket.setFillColor(sf::Color::Black);
            pocket.setOrigin(pocketRadius, pocketRadius);
            pocket.setPosition(pPos);
            window.draw(pocket);
        }

        window.draw(cueBall.shape);
        if (hasFont) {
            sf::Text t;
            t.setFont(font);
            t.setString("0");
            t.setCharacterSize(14);
            t.setFillColor(sf::Color::Black);
            t.setPosition(cueBall.shape.getPosition().x - 4.f, cueBall.shape.getPosition().y - 9.f);
            window.draw(t);
        }

        for (auto& b : rackBalls) {
            window.draw(b.shape);
            if (hasFont) {
                sf::Text t;
                t.setFont(font);
                t.setString(std::to_string(b.number));
                t.setCharacterSize(12);
                t.setFillColor(b.number == 8 ? sf::Color::White : sf::Color::Black);
                t.setPosition(b.shape.getPosition().x - 4.f, b.shape.getPosition().y - 8.f);
                window.draw(t);
            }
        }

        window.display();
    }

    return 0;
}