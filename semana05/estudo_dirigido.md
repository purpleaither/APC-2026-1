# Estudo Dirigido

## Classificação de Triângulos

definir funcao_classificacao_triangulos:

  angulo1 = real ("Insira o 1o angulo aqui")
  
  angulo2 = real ("Insira o 2o angulo aqui")
  
  angulo3 = real ("Insira o 3o angulo aqui")

se angulo1 + angulo2 + angulo3 == 180:

  se angulo1 igual à angulo2 e igual à angulo3:
  
    saida("Este triângulo é equilátero.")

  senao se angulo1 diferente de angulo2 e angulo1 diferente de angulo3 e angulo2 diferente de angulo3:
    
    saida("Este triângulo é escaleno.")
    
  senao:
    
    saida("Este triângulo é isósceles.")
    
senao:
  
  saida("Ângulos incorretos! Por favor, insira novamente.")
  
  retorne funcao_classificacao_triangulos()





