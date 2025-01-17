#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# pylint: disable=invalid-name

"""
Biblioteca Gráfica / Graphics Library.

Desenvolvido por: Gabriel Duarte & Michel Moraes
Disciplina: Computação Gráfica
Data:
"""

import time         # Para operações com tempo

import gpu          # Simula os recursos de uma GPU
import numpy as np
import math

class GL:
    """Classe que representa a biblioteca gráfica (Graphics Library)."""

    width = 800   # largura da tela
    height = 600  # altura da tela
    near = 0.01   # plano de corte próximo
    far = 1000    # plano de corte distante

    @staticmethod
    def setup(width, height, near=0.01, far=1000):
        """Definr parametros para câmera de razão de aspecto, plano próximo e distante."""
        GL.width = width
        GL.height = height
        GL.near = near
        GL.far = far
        GL.screen = np.matrix([
            [width / 2, 0, 0, width / 2], 
            [0, - height / 2, 0, height / 2],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        GL.zBuffer = [[None for x in range(GL.width)] for y in range(GL.height)]
        GL.pilha = []
        GL.anim = False
        

    @staticmethod
    def transform_point(points):
        screen_points = []
        for i in range(0, len(points) - 2, 3):
            p = np.matrix([[points[i]], [points[i+1]], [points[i+2]], [1]])
            norm = GL.matrix_mvp.dot(p)
            norm = np.divide(norm, norm[3][0])
            screen_points += [GL.screen.dot(norm)]
        return screen_points

    @staticmethod
    def triangleSet(point, colors):
        print("roda triangleSet")
        """Função usada para renderizar TriangleSet."""
        # Nessa função você receberá pontos no parâmetro point, esses pontos são uma lista
        # de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x do
        # primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e
        # assim por diante.
        # No TriangleSet os triângulos são informados individualmente, assim os três
        # primeiros pontos definem um triângulo, os três próximos pontos definem um novo
        # triângulo, e assim por diante.
        # O parâmetro colors é um dicionário com os tipos cores possíveis, para o TriangleSet
        # você pode assumir o desenho das linhas com a cor emissiva (emissiveColor).

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TriangleSet : pontos = {0}".format(point)) # imprime no terminal pontos
        print("TriangleSet : colors = {0}".format(colors)) # imprime no terminal as cores
        # print(len(point))
        
        point = GL.transform_point(point)
        # print(point)

        for p in range(0, len(point)-2, 3):
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)
            
            tri = [
                [point[p][0],point[p][1], point[p][2]],
                [point[p+1][0],point[p+1][1], point[p+1][2]],
                [point[p+2][0],point[p+2][1], point[p+2][2]],

            ]
            max_min = GL.Max_min_tri(tri)
            for x in range(max_min[0], max_min[1]):
                for y in range(max_min[2], max_min[3]):
                    if GL.inside(tri, x ,y)[0]:
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

        # # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

    @staticmethod
    def viewpoint(position, orientation, fieldOfView):
        print("roda view Point")

        """Função usada para renderizar (na verdade coletar os dados) de Viewpoint."""
        # Na função de viewpoint você receberá a posição, orientação e campo de visão da
        # câmera virtual. Use esses dados para poder calcular e criar a matriz de projeção
        # perspectiva para poder aplicar nos pontos dos objetos geométricos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Viewpoint : ", end='')
        print("position = {0} ".format(position), end='')
        print("orientation = {0} ".format(orientation), end='')
        print("fieldOfView = {0} ".format(fieldOfView))

        fovy = 2 * math.atan(math.tan(fieldOfView / 2) * GL.height / math.sqrt(GL.height ** 2 + GL.width ** 2))
        top = GL.near * math.tan(fovy)
        right = top * GL.width / GL.height

        GL.perspectiva = np.matrix([
            [GL.near / right, 0, 0, 0], 
            [0, GL.near / top, 0, 0],
            [0, 0, -((GL.far + GL.near) / (GL.far - GL.near)), ((- 2 * GL.far * GL.near)/(GL.far - GL.near))],
            [0, 0, -1, 0]])

        translation_matrix = np.matrix([
            [1, 0, 0, position[0]], 
            [0, 1, 0, position[1]],
            [0, 0, 1, position[2]],
            [0, 0, 0, 1]
        ])

        translation_matrix_inv = np.linalg.inv(translation_matrix)

        if orientation:
            if (orientation[1] > 0):
                rotation_matrix = np.array([[np.cos(orientation[3]),0,np.sin(orientation[3]),0],
                                            [0,1,0,0],
                                            [-np.sin(orientation[3]),0,np.cos(orientation[3]),0],
                                            [0,0,0,1]])
            elif (orientation[0] > 0):
                rotation_matrix = np.array([[ 1,0,0,0],
                                            [ 0, np.cos(orientation[3]),-np.sin(orientation[3]),0],
                                            [ 0, np.sin(orientation[3]),np.cos(orientation[3]),0],
                                            [ 0,0,0,1]])
            else:     
                rotation_matrix = np.array([[np.cos(orientation[3]),-np.sin(orientation[3]),0,0],
                                            [np.sin(orientation[3]),np.cos(orientation[3]),0,0],
                                            [0,0,1,0],
                                            [0,0,0,1]])

            rotation_matrix_inv = np.linalg.inv(rotation_matrix)
        
        GL.lookat = rotation_matrix_inv.dot(translation_matrix_inv)



    @staticmethod
    def transform_in(translation, scale, rotation):
        print("roda transform in")

        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_in será chamada quando se entrar em um nó X3D do tipo Transform
        # do grafo de cena. Os valores passados são a escala em um vetor [x, y, z]
        # indicando a escala em cada direção, a translação [x, y, z] nas respectivas
        # coordenadas e finalmente a rotação por [x, y, z, t] sendo definida pela rotação
        # do objeto ao redor do eixo x, y, z por t radianos, seguindo a regra da mão direita.
        # Quando se entrar em um nó transform se deverá salvar a matriz de transformação dos
        # modelos do mundo em alguma estrutura de pilha.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Transform : ", end='')
        if translation:
            print("translation = {0} ".format(translation), end='') # imprime no terminal
        if scale:
            print("scale = {0} ".format(scale), end='') # imprime no terminal
        if rotation:
            print("rotation = {0} ".format(rotation), end='') # imprime no terminal
        print("")

        scale_matrix = np.matrix([
            [scale[0], 0, 0, 0], 
            [0, scale[1], 0, 0],
            [0, 0, scale[2], 0],
            [0, 0, 0, 1]])

        translation_matrix = np.matrix([
            [1, 0, 0, translation[0]], 
            [0, 1, 0, translation[1]],
            [0, 0, 1, translation[2]],
            [0, 0, 0, 1]])


        if rotation:
            if (rotation[1] > 0):
                rotation_matrix = np.array([[  np.cos(rotation[3]), 0, np.sin(rotation[3]), 0],
                                            [0, 1,0, 0],
                                            [ -np.sin(rotation[3]), 0, np.cos(rotation[3]), 0],
                                            [0, 0,                      0, 1]])
            elif (rotation[0] > 0):
                rotation_matrix = np.array([[ 1,                      0,                       0, 0],
                                            [ 0, np.cos(rotation[3]), -np.sin(rotation[3]), 0],
                                            [ 0, np.sin(rotation[3]),  np.cos(rotation[3]), 0],
                                            [ 0,                      0,                       0, 1]])
            
            else:     
                rotation_matrix = np.array([[ np.cos(rotation[3]), -np.sin(rotation[3]), 0, 0],
                                            [ np.sin(rotation[3]),  np.cos(rotation[3]), 0, 0],
                                            [                      0,                       0, 1, 0],
                                            [0,0,0,1]])

        GL.model_world = translation_matrix.dot(rotation_matrix).dot(scale_matrix)

        if (len(GL.pilha) > 1):
            GL.model_world = np.matmul(GL.pilha[-1], GL.model_world)

        GL.pilha.append(GL.model_world)
        GL.matrix_mvp = GL.perspectiva.dot(GL.lookat).dot(GL.model_world)


    @staticmethod
    def transform_out():
        print("roda tranform out")

        """Função usada para renderizar (na verdade coletar os dados) de Transform."""
        # A função transform_out será chamada quando se sair em um nó X3D do tipo Transform do
        # grafo de cena. Não são passados valores, porém quando se sai de um nó transform se
        # deverá recuperar a matriz de transformação dos modelos do mundo da estrutura de
        # pilha implementada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        if (len(GL.pilha) > 0):
            GL.pilha.pop()
        
        print("Saindo de Transform")

    @staticmethod
    def triangleStripSet(point, stripCount, colors):
        print("roda triangleStripSet")

        """Função usada para renderizar TriangleStripSet."""
        # A função triangleStripSet é usada para desenhar tiras de triângulos interconectados,
        # você receberá as coordenadas dos pontos no parâmetro point, esses pontos são uma
        # lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor da coordenada x
        # do primeiro ponto, point[1] o valor y do primeiro ponto, point[2] o valor z da
        # coordenada z do primeiro ponto. Já point[3] é a coordenada x do segundo ponto e assim
        # por diante. No TriangleStripSet a quantidade de vértices a serem usados é informado
        # em uma lista chamada stripCount (perceba que é uma lista). Ligue os vértices na ordem,
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        # print("TriangleStripSet : pontos = {0} ".format(point), end='')
        # for i, strip in enumerate(stripCount):
        #     print("strip[{0}] = {1} ".format(i, strip), end='')
        # print("")
        # print("TriangleStripSet : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel
        point = GL.transform_point(point)
        tri = []
        for i in range(stripCount[0] - 2):

            tri = [
                [point[i + 2][0], point[i + 2][1], point[i + 2][2]],
                [point[i + 1][0], point[i + 1][1], point[i + 1][2]], 
                [point[i][0], point[i][1], point[i][2]], 
            ]
            if i % 2 == 0: 
                tri = [
                    [point[i][0], point[i][1], point[i][2]], 
                    [point[i + 1][0], point[i + 1][1], point[i + 1][2]], 
                    [point[i + 2][0], point[i + 2][1], point[i + 2][2]],
                    ]

            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)

            max_min = GL.Max_min_tri(tri)
            for x in range(max_min[0], max_min[1]):
                for y in range(max_min[2], max_min[3]):
                    if GL.inside(tri, x ,y)[0]:
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

    @staticmethod
    def indexedTriangleStripSet(point, index, colors):
        print("roda indexedTriangleStripSet")

        """Função usada para renderizar IndexedTriangleStripSet."""
        # A função indexedTriangleStripSet é usada para desenhar tiras de triângulos
        # interconectados, você receberá as coordenadas dos pontos no parâmetro point, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim point[0] é o valor
        # da coordenada x do primeiro ponto, point[1] o valor y do primeiro ponto, point[2]
        # o valor z da coordenada z do primeiro ponto. Já point[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedTriangleStripSet uma lista informando
        # como conectar os vértices é informada em index, o valor -1 indica que a lista
        # acabou. A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante. Cuidado com a orientação dos vértices, ou seja,
        # todos no sentido horário ou todos no sentido anti-horário, conforme especificado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedTriangleStripSet : pontos = {0}, index = {1}".format(point, index))
        print("IndexedTriangleStripSet : colors = {0}".format(colors)) # imprime as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        point = GL.transform_point(point)
        tri = []
        for i in range(len(index) - 3):
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)

            tri = [
                [point[index[i + 2]][0], point[index[i + 2]][1], point[index[i + 2]][2]], 
                [point[index[i + 1]][0], point[index[i + 1]][1], point[index[i + 1]][2]], 
                [point[index[i]][0], point[index[i]][1], point[index[i]][2]], 
            ]
            if i % 2 == 0: 
                tri = [
                    [point[index[i]][0], point[index[i]][1], point[index[i]][2]], 
                    [point[index[i + 1]][0], point[index[i + 1]][1], point[index[i + 1]][2]], 
                    [point[index[i + 2]][0], point[index[i + 2]][1], point[index[i + 2]][2]], 
                    ]
            max_min = GL.Max_min_tri(tri)
            for x in range(max_min[0], max_min[1]):
                for y in range(max_min[2], max_min[3]):
                    if GL.inside(tri, x ,y)[0]:
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

    @staticmethod
    def box(size, colors):
        print("roda box")

        """Função usada para renderizar Boxes."""
        # A função box é usada para desenhar paralelepípedos na cena. O Box é centrada no
        # (0, 0, 0) no sistema de coordenadas local e alinhado com os eixos de coordenadas
        # locais. O argumento size especifica as extensões da caixa ao longo dos eixos X, Y
        # e Z, respectivamente, e cada valor do tamanho deve ser maior que zero. Para desenha
        # essa caixa você vai provavelmente querer tesselar ela em triângulos, para isso
        # encontre os vértices e defina os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Box : size = {0}".format(size)) # imprime no terminal pontos
        print("Box : colors = {0}".format(colors)) # imprime no terminal as cores

        # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        points = [-size[0], -size[1],  size[2], 
                   size[0], -size[1],  size[2], 
                   size[0],  size[1],  size[2], 
                  -size[0],  size[1],  size[2],
                  -size[0],  size[1], -size[2],
                   size[0],  size[1], -size[2],
                  -size[0], -size[1], -size[2],
                   size[0], -size[1], -size[2]]

        pontos = GL.transform_point(points)

        tri = [
                [pontos[1], pontos[7], pontos[5]], 
                [pontos[5], pontos[2], pontos[1]],
                [pontos[2], pontos[3], pontos[0]], 
                [pontos[0], pontos[1], pontos[2]],
                [pontos[3], pontos[2], pontos[5]], 
                [pontos[4], pontos[3], pontos[0]], 
                [pontos[5], pontos[4], pontos[3]], 
                [pontos[4], pontos[5], pontos[6]], 
                [pontos[6], pontos[4], pontos[0]], 
                [pontos[5], pontos[6], pontos[7]],
                [pontos[7], pontos[6], pontos[0]],
                [pontos[7], pontos[1], pontos[0]] 
                ]
        for t in tri:
            r=int(colors['diffuseColor'][0]*255)
            g=int(colors['diffuseColor'][1]*255)
            b=int(colors['diffuseColor'][2]*255)
            max_min = GL.Max_min_tri(t)
            for x in range(max_min[0], max_min[1]):
                for y in range(max_min[2], max_min[3]):
                    if GL.inside(t, x ,y):
                        # gpu.GPU.set_pixel(x, y, r, g, b)
                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  # altera pixel

    @staticmethod
    def inside(vertices, x, y):
        # print(f'\nINSIDE: \n{vertices}\n X: {x} \n Y: {y}')
        x1, x2, x3 = vertices[0][0][0], vertices[1][0][0], vertices[2][0][0]
        y1, y2, y3 = vertices[0][1][0], vertices[1][1][0], vertices[2][1][0]
        z1, z2, z3 = vertices[0][2][0], vertices[1][2][0], vertices[2][2][0]

        L1 = (y2-y1)*x - (x2-x1)*y + y1*(x2-x1) - x1*(y2-y1)
        L2 = (y3-y2)*x - (x3-x2)*y + y2*(x3-x2) - x2*(y3-y2)
        L3 = (y1-y3)*x - (x1-x3)*y + y3*(x1-x3) - x3*(y1-y3)

        alpha, beta, gamma, z = 0, 0, 0, 0
        
        if (-(x1 - x2) * (y3 - y2) + (y1 - y2) * (x3 - x2)) != 0 or (-(x2 - x3) * (y1 - y3) + (y2 - y3) * (x1 - x3)) != 0:
            alpha = (-(x - x2) * (y3 - y2) + (y - y2) * (x3 - x2)) / (-(x1 - x2) * (y3 - y2) + (y1 - y2) * (x3 - x2))    
            beta  = (-(x - x3) * (y1 - y3) + (y - y3) * (x1 - x3)) / (-(x2 - x3) * (y1 - y3) + (y2 - y3) * (x1 - x3))
            gamma = 1 - (alpha + beta)
            z = 1 / (alpha * (1 / z1) + beta * (1 / z2) + gamma * (1 / z3))
            
        insido = (L1 >= 0 and L2 >= 0 and L3 >= 0)
        return [insido, alpha, beta, gamma, z]


    @staticmethod
    def indexedFaceSet(coord, coordIndex, colorPerVertex, color, colorIndex,
                       texCoord, texCoordIndex, colors, current_texture):        
        """Função usada para renderizar IndexedFaceSet."""
        # A função indexedFaceSet é usada para desenhar malhas de triângulos. Ela funciona de
        # forma muito simular a IndexedTriangleStripSet porém com mais recursos.
        # Você receberá as coordenadas dos pontos no parâmetro cord, esses
        # pontos são uma lista de pontos x, y, e z sempre na ordem. Assim coord[0] é o valor
        # da coordenada x do primeiro ponto, coord[1] o valor y do primeiro ponto, coord[2]
        # o valor z da coordenada z do primeiro ponto. Já coord[3] é a coordenada x do
        # segundo ponto e assim por diante. No IndexedFaceSet uma lista de vértices é informada
        # em coordIndex, o valor -1 indica que a lista acabou.
        # A ordem de conexão será de 3 em 3 pulando um índice. Por exemplo: o
        # primeiro triângulo será com os vértices 0, 1 e 2, depois serão os vértices 1, 2 e 3,
        # depois 2, 3 e 4, e assim por diante.
        # Adicionalmente essa implementação do IndexedFace aceita cores por vértices, assim
        # se a flag colorPerVertex estiver habilitada, os vértices também possuirão cores
        # que servem para definir a cor interna dos poligonos, para isso faça um cálculo
        # baricêntrico de que cor deverá ter aquela posição. Da mesma forma se pode definir uma
        # textura para o poligono, para isso, use as coordenadas de textura e depois aplique a
        # cor da textura conforme a posição do mapeamento. Dentro da classe GPU já está
        # implementadado um método para a leitura de imagens.

        # Os prints abaixo são só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("IndexedFaceSet : ")
        if coord:
            print("\tpontos(x, y, z) = {0}, coordIndex = {1}".format(coord, coordIndex))
        print("colorPerVertex = {0}".format(colorPerVertex))
        if colorPerVertex and color and colorIndex:
            print("\tcores(r, g, b) = {0}, colorIndex = {1}".format(color, colorIndex))
        if texCoord and texCoordIndex:
            print("\tpontos(u, v) = {0}, texCoordIndex = {1}".format(texCoord, texCoordIndex))
        if current_texture:
            image = gpu.GPU.load_texture(current_texture[0])
            print("\t Matriz com image = {0}".format(image))
            print("\t Dimensões da image = {0}".format(image.shape))
        print("IndexedFaceSet : colors = {0}".format(colors))  # imprime no terminal as cores

        # # Exemplo de desenho de um pixel branco na coordenada 10, 10
        # gpu.GPU.draw_pixels([10, 10], gpu.GPU.RGB8, [255, 255, 255])  # altera pixel

        point = GL.transform_point(coord)
        cor = []
        tri = []

        if colorPerVertex and colorIndex and color:
            cores = []
            for c in range(0, len(color), 3): 
                cores.append([color[c], color[c + 1], color[c + 2]])

            for i in range(len(coordIndex)):
                if coordIndex[i] < 0 or colorIndex[i] < 0:
                    max_min = GL.Max_min_tri(tri)
                    for x in range(max_min[0], max_min[1]):
                        for y in range(max_min[2], max_min[3]):
                            res = GL.inside(tri, x, y)
                            is_inside, alpha, beta, gamma, z = res[0], res[1], res[2], res[3], res[4]    

                            r = int(colors["diffuseColor"][0]*255)
                            g = int(colors["diffuseColor"][1]*255)
                            b = int(colors["diffuseColor"][2]*255)
                            
                            if is_inside:
                                if colorPerVertex and cor:
                                    r = (cor[0][0] * alpha + cor[1][0] * beta + cor[2][0] * gamma) * 255
                                    g = (cor[0][1] * alpha + cor[1][1] * beta + cor[2][1] * gamma) * 255
                                    b = (cor[0][2] * alpha + cor[1][2] * beta + cor[2][2] * gamma) * 255
                                
                                if (GL.zBuffer[y][x]):
                                    if (z <= GL.zBuffer[y][x]):
                                        GL.zBuffer[y][x] = z
                                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  
                                else:
                                    GL.zBuffer[y][x] = z
                                    gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])

                    tri = []
                    cor = []
                else:
                    cor.append(cores[colorIndex[i]])
                    tri.append(point[coordIndex[i]])

        elif (texCoord and texCoordIndex):
            p_tex = []
            for p in range(0, len(texCoord), 2):
                p_tex.append([texCoord[p], texCoord[p+1]])
            tex = []

            for i in range(len(coordIndex)):
                if coordIndex[i] < 0:
                    max_min = GL.Max_min_tri(tri)
                    for x in range(max_min[0], max_min[1]):
                        for y in range(max_min[2], max_min[3]):
                            res = GL.inside(tri, x, y)
                            is_inside, alpha, beta, gamma, z = res[0], res[1], res[2], res[3], res[4]

                            r = int(colors["diffuseColor"][0]*255)
                            g = int(colors["diffuseColor"][1]*255)
                            b = int(colors["diffuseColor"][2]*255)
                            
                            if is_inside:
                                tex_x = (tex[0][0] * alpha + tex[1][0] * beta + tex[2][0] * gamma) * image.shape[0]
                                tex_y = (tex[0][1] * alpha + tex[1][1] * beta + tex[2][1] * gamma) * image.shape[1]
                                r, g, b, a = image[int(-tex_y)][int(tex_x)]
                                
                                if (GL.zBuffer[y][x]):
                                    if (z <= GL.zBuffer[y][x]):
                                        GL.zBuffer[y][x] = z
                                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  
                                else:
                                    GL.zBuffer[y][x] = z
                                    gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])

                    tri = []
                    tex = []
                else:
                    tri.append(point[coordIndex[i]])
                    tex.append(p_tex[texCoordIndex[i]])
        else:
            
            for i in range(len(coordIndex)):
                if coordIndex[i] < 0:
                    max_min = GL.Max_min_tri(tri)
                    for x in range(max_min[0], max_min[1]):
                        for y in range(max_min[2], max_min[3]):
                            res = GL.inside(tri, x, y)
                            is_inside, alpha, beta, gamma, z = res[0], res[1], res[2], res[3], res[4]
                            r = int(colors["diffuseColor"][0]*255)
                            g = int(colors["diffuseColor"][1]*255)
                            b = int(colors["diffuseColor"][2]*255)
                            
                            if is_inside:
                                if GL.anim:
                                    gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])
                                else:
                                    if (GL.zBuffer[y][x]):
                                        if (z <= GL.zBuffer[y][x]):
                                            GL.zBuffer[y][x] = z
                                            gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])  
                                    else:
                                        GL.zBuffer[y][x] = z
                                        gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])
                    tri = []
                else:
                    tri.append(point[coordIndex[i]])
    @staticmethod
    def sphere(radius, colors):
        """Função usada para renderizar Esferas."""
        # A função sphere é usada para desenhar esferas na cena. O esfera é centrada no
        # (0, 0, 0) no sistema de coordenadas local. O argumento radius especifica o
        # raio da esfera que está sendo criada. Para desenha essa esfera você vai
        # precisar tesselar ela em triângulos, para isso encontre os vértices e defina
        # os triângulos.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Sphere : radius = {0}".format(radius)) # imprime no terminal o raio da esfera
        print("Sphere : colors = {0}".format(colors)) # imprime no terminal as cores
        
        count = 12
        theta_list = []
        for theta in range(0, 2 * (count) + 1, 1):
            theta_list.append((theta/count)*math.pi)

        phi_list = []
        for phi in range(-count, count + 1, 1):
            phi_list.append((phi/count) * math.pi / 2)

        pontos = []

        for n in range(len(phi_list) - 1):
            for j in range(len(theta_list)):
                x = radius * math.sin(phi_list[n]) * math.cos(theta_list[j])
                y = radius * math.sin(phi_list[n]) * math.sin(theta_list[j])
                z = radius * math.cos(phi_list[n])

                x2 = radius * math.sin(phi_list[n + 1]) * math.cos(theta_list[j])
                y2 = radius * math.sin(phi_list[n + 1]) * math.sin(theta_list[j])
                z2 = radius * math.cos(phi_list[n + 1])

                pontos.extend([x, y, z, x2, y2, z2])
        
        stripCount = [int(len(pontos)/3)]

        point = GL.transform_point(pontos)
        tri = []
        for i in range(stripCount[0] - 2):

            tri = [
                [point[i + 2][0], point[i + 2][1], point[i + 2][2]],
                [point[i + 1][0], point[i + 1][1], point[i + 1][2]], 
                [point[i][0], point[i][1], point[i][2]], 
            ]
            if i % 2 == 0: 
                tri = [
                    [point[i][0], point[i][1], point[i][2]], 
                    [point[i + 1][0], point[i + 1][1], point[i + 1][2]], 
                    [point[i + 2][0], point[i + 2][1], point[i + 2][2]],
                    ]
            if GL.light['hasLight']:
                x_list = [float(tri[0][0]), float(tri[1][0]), float(tri[2][0])]
                y_list = [float(tri[0][1]), float(tri[1][1]), float(tri[2][1])]
                z_list = [float(tri[0][2]), float(tri[1][2]), float(tri[2][2])]
                
                U = [
                    x_list[2] - x_list[0],
                    y_list[2] - y_list[0],
                    z_list[2] - z_list[0],
                ]
                V = [
                    x_list[1] - x_list[0],
                    y_list[1] - y_list[0],
                    z_list[1] - z_list[0],
                ]
                
                N = np.cross(U, V)-1
                
                N = np.divide(N, np.linalg.norm(N))
                
                L = []
                for dir in GL.light['direction']:
                    L.append(dir * (-1))
                    
                NL = np.dot(N, L)
                
                ambient = []
                diffuse = []
                specular = []

                for cor in colors["diffuseColor"]: 
                    ambient.append(cor * (GL.light['ambientIntensity'] * colors["shininess"]))
                    diffuse.append(cor * GL.light['intensity'] * NL)

                a = np.add(np.array(L), np.array([0, 0, 1]))
                b = np.divide(a, np.linalg.norm(a))  
                c = (np.dot(b, N)) ** (colors["shininess"] * 128)
                for x in colors["specularColor"]:
                    specular.append(x * GL.light['ambientIntensity'] * c)

                rgb = []
                for i in range(len(GL.light['color'])):
                    c =  (GL.light['color'][i] * (ambient[i] + diffuse[i] + specular[i])) + colors["emissiveColor"][i]
                    rgb.append(c)
                
                r = rgb[0] * 255
                g = rgb[1] * 255
                b = rgb[2] * 255
                        
            max_min = GL.Max_min_tri(tri)
            for x in range(max_min[0], max_min[1]):
                for y in range(max_min[2], max_min[3]):
                    res = GL.inside(tri, x, y)
                    is_inside, alpha, beta, gamma, z = res[0], res[1], res[2], res[3], res[4]
                    
                    if is_inside:
                        if GL.light['hasLight']:
                            gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])
                        else:
                            r=int(colors['diffuseColor'][0]*255)
                            g=int(colors['diffuseColor'][1]*255)
                            b=int(colors['diffuseColor'][2]*255)
                            gpu.GPU.draw_pixels([x, y], gpu.GPU.RGB8, [r, g, b])
                 

    @staticmethod
    def navigationInfo(headlight):
        """Características físicas do avatar do visualizador e do modelo de visualização."""
        # O campo do headlight especifica se um navegador deve acender um luz direcional que
        # sempre aponta na direção que o usuário está olhando. Definir este campo como TRUE
        # faz com que o visualizador forneça sempre uma luz do ponto de vista do usuário.
        # A luz headlight deve ser direcional, ter intensidade = 1, cor = (1 1 1),
        # ambientIntensity = 0,0 e direção = (0 0 −1).

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("NavigationInfo : headlight = {0}".format(headlight)) # imprime no terminal

    @staticmethod
    def directionalLight(ambientIntensity, color, intensity, direction):
        """Luz direcional ou paralela."""
        # Define uma fonte de luz direcional que ilumina ao longo de raios paralelos
        # em um determinado vetor tridimensional. Possui os campos básicos ambientIntensity,
        # cor, intensidade. O campo de direção especifica o vetor de direção da iluminação
        # que emana da fonte de luz no sistema de coordenadas local. A luz é emitida ao
        # longo de raios paralelos de uma distância infinita.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("DirectionalLight : ambientIntensity = {0}".format(ambientIntensity))
        print("DirectionalLight : color = {0}".format(color)) # imprime no terminal
        print("DirectionalLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("DirectionalLight : direction = {0}".format(direction)) # imprime no terminal

        GL.light = {
            "hasLight": True,
            "ambientIntensity" : ambientIntensity,
            "color" : color,
            "intensity" : intensity,
            "direction" : direction
        }


    @staticmethod
    def pointLight(ambientIntensity, color, intensity, location):
        """Luz pontual."""
        # Fonte de luz pontual em um local 3D no sistema de coordenadas local. Uma fonte
        # de luz pontual emite luz igualmente em todas as direções; ou seja, é omnidirecional.
        # Possui os campos básicos ambientIntensity, cor, intensidade. Um nó PointLight ilumina
        # a geometria em um raio de sua localização. O campo do raio deve ser maior ou igual a
        # zero. A iluminação do nó PointLight diminui com a distância especificada.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("PointLight : ambientIntensity = {0}".format(ambientIntensity))
        print("PointLight : color = {0}".format(color)) # imprime no terminal
        print("PointLight : intensity = {0}".format(intensity)) # imprime no terminal
        print("PointLight : location = {0}".format(location)) # imprime no terminal

    @staticmethod
    def fog(visibilityRange, color):
        """Névoa."""
        # O nó Fog fornece uma maneira de simular efeitos atmosféricos combinando objetos
        # com a cor especificada pelo campo de cores com base nas distâncias dos
        # vários objetos ao visualizador. A visibilidadeRange especifica a distância no
        # sistema de coordenadas local na qual os objetos são totalmente obscurecidos
        # pela névoa. Os objetos localizados fora de visibilityRange do visualizador são
        # desenhados com uma cor de cor constante. Objetos muito próximos do visualizador
        # são muito pouco misturados com a cor do nevoeiro.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("Fog : color = {0}".format(color)) # imprime no terminal
        print("Fog : visibilityRange = {0}".format(visibilityRange))

    @staticmethod
    def timeSensor(cycleInterval, loop):
        """Gera eventos conforme o tempo passa."""
        # Os nós TimeSensor podem ser usados para muitas finalidades, incluindo:
        # Condução de simulações e animações contínuas; Controlar atividades periódicas;
        # iniciar eventos de ocorrência única, como um despertador;
        # Se, no final de um ciclo, o valor do loop for FALSE, a execução é encerrada.
        # Por outro lado, se o loop for TRUE no final de um ciclo, um nó dependente do
        # tempo continua a execução no próximo ciclo. O ciclo de um nó TimeSensor dura
        # cycleInterval segundos. O valor de cycleInterval deve ser maior que zero.

        # Deve retornar a fração de tempo passada em fraction_changed

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("TimeSensor : cycleInterval = {0}".format(cycleInterval)) # imprime no terminal
        print("TimeSensor : loop = {0}".format(loop))

        # Esse método já está implementado para os alunos como exemplo
        epoch = time.time()  # time in seconds since the epoch as a floating point number.
        fraction_changed = (epoch % cycleInterval) / cycleInterval

        return fraction_changed
    

    @staticmethod
    def splinePositionInterpolator(set_fraction, key, keyValue, closed):
        """Interpola não linearmente entre uma lista de vetores 3D."""
        # Interpola não linearmente entre uma lista de vetores 3D. O campo keyValue possui
        # uma lista com os valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantos vetores 3D quanto os
        # quadros-chave no key. O campo closed especifica se o interpolador deve tratar a malha
        # como fechada, com uma transições da última chave para a primeira chave. Se os keyValues
        # na primeira e na última chave não forem idênticos, o campo closed será ignorado.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("SplinePositionInterpolator : set_fraction = {0}".format(set_fraction))
        print("SplinePositionInterpolator : key = {0}".format(key)) # imprime no terminal
        print("SplinePositionInterpolator : keyValue = {0}".format(keyValue))
        print("SplinePositionInterpolator : closed = {0}".format(closed))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        GL.anim = True

        s = 0
        size = 3

        for k in range(len(key)):
            if set_fraction < key[k]:
                k -= 1
                s = (set_fraction - key[k]) / (key[k + 1] - key[k])
                break

        inter1 = (k) * size
        inter2 = (k + 1) * size
        inter3 = (k + 2) * size
        inter4 = (k - 1) * size

        if inter2 >= len(keyValue):
            if closed:
                inter2 = 0
                inter3 = size
            else:
                 return [0, 0, 0]

        if inter3 >= len(keyValue):
            if not closed: 
                inter3 = 0
            else:
                return [0, 0, 0]

        if inter4 >= 0:
            inter4 = keyValue[inter4 : inter4 + size]
        else:
            inter4 = [0, 0, 0]

        inter1 = keyValue[inter1 : inter1 + size]
        inter2 = keyValue[inter2 : inter2 + size]
        inter3 = keyValue[inter3 : inter3  + size]

        T0 = []
        T1 = []
        for i in range(size):
            T0.append((inter2[i] - inter4[i]) / 2)
            T1.append((inter3[i] - inter1[i]) / 2)

        hermite = np.matrix([
            [2, -2, 1, 1], 
            [-3, 3, -2, -1],
            [0, 0, 1, 0],
            [1, 0, 0, 0]
        ])

        S = np.matrix([[s ** 3, s ** 2, s, 1]])
        C = np.matrix([inter1, inter2, T0, T1])

        value_changed = np.dot(S, np.dot(hermite, C)).tolist()

        return value_changed[0]


    @staticmethod
    def orientationInterpolator(set_fraction, key, keyValue):
        """Interpola entre uma lista de valores de rotação especificos."""
        # Interpola rotações são absolutas no espaço do objeto e, portanto, não são cumulativas.
        # Uma orientação representa a posição final de um objeto após a aplicação de uma rotação.
        # Um OrientationInterpolator interpola entre duas orientações calculando o caminho mais
        # curto na esfera unitária entre as duas orientações. A interpolação é linear em
        # comprimento de arco ao longo deste caminho. Os resultados são indefinidos se as duas
        # orientações forem diagonalmente opostas. O campo keyValue possui uma lista com os
        # valores a serem interpolados, key possui uma lista respectiva de chaves
        # dos valores em keyValue, a fração a ser interpolada vem de set_fraction que varia de
        # zeroa a um. O campo keyValue deve conter exatamente tantas rotações 3D quanto os
        # quadros-chave no key.

        # O print abaixo é só para vocês verificarem o funcionamento, DEVE SER REMOVIDO.
        print("OrientationInterpolator : set_fraction = {0}".format(set_fraction))
        print("OrientationInterpolator : key = {0}".format(key)) # imprime no terminal
        print("OrientationInterpolator : keyValue = {0}".format(keyValue))

        # Abaixo está só um exemplo de como os dados podem ser calculados e transferidos
        value_changed = [0, 0, 1, 0]

        return value_changed


    @staticmethod
    def Max_min_tri(tri):
        x = [tri[0][0], tri[1][0], tri[2][0]]
        y = [tri[0][1], tri[1][1], tri[2][1]]
        return [int(min(x)), int(max(x))+1, int(min(y)), int(max(y))+1]

    # Para o futuro (Não para versão atual do projeto.)
    def vertex_shader(self, shader):
        """Para no futuro implementar um vertex shader."""

    def fragment_shader(self, shader):
        """Para no futuro implementar um fragment shader."""