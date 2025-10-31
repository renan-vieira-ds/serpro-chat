import sys

from search import search_prompt

def main():
   question = input("Digite sua pergunta pergunta relatica ao concurso SERPRO 2023: \n")

   chain = search_prompt(question)    

   print(chain)


if __name__ == "__main__":
    main()
