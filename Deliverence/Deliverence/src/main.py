import sys
import os

# Tambahkan folder 'src/' dan root folder ke sys.path agar import lokal maupun paket berjalan lancar
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)
sys.path.insert(1, os.path.dirname(src_dir))

from game import Game

if __name__ == '__main__':
    game = Game()
    game.run()
