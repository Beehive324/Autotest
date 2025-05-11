import click
import requests
from pyfiglet import Figlet

f = Figlet(font='slant')


__author__ = "Fairson Soares"


#reconnaisance phase tool
def reconnaisance():
    pass

#maintaining access tool
def maintaining_access():
    pass


#scanning tool
@click.command()
def scan(target):
    pass

#attack tool
@click.command()
def attack(target):
    pass


#reporint tool
@click.command()
def reporting():
    pass

@click.command()
def main():
    pass
    #main implementation of multi agent framework for pentesitng 


if __name__ == '__main__':
    print(f.renderText('AutoTest'))
   






