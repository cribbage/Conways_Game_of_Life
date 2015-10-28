import pygame, math, sys, random, time, random, copy, gc
from pygame.locals import *

TILESIZE = (6,6)
GRIDSIZE = (1200,600)
SHAPES = [None,'g','ge']
GLIDER = ((False,None,1,1),(True,None,1,1),(True,False,1,1),(None,False,1,2))
GLIDEREMITTER = ((False,None,1,1),(False,False,1,1,),(False,True,1,1),(False,True,2,2),(False,False,2,2),(False,None,3,1),(False,True,4,3),(False,False,4,3),(False,False,5,3),(False,True,5,3),(False,True,6,2),(False,False,6,2),(False,False,7,1),(False,True,7,1),(False,None,7,1),(False,None,17,1),(False,None,16,1),(False,False,17,1),(False,False,16,1),(True,False,3,1),(True,False,4,1),(True,False,3,2),(True,False,4,2),(True,False,3,3),(True,False,4,3),(True,None,5,1),(True,False,5,4),(True,False,7,4),(True,None,7,1),(True,False,7,5),(True,True,7,1),(True,False,17,3),(True,False,17,2),(True,False,18,2),(True,False,18,3))
FPS = 20

class Node:
	def __init__(self,pos):
		self.pos = pos
		self.alive = False
		self.color = (0,80,0)	
		
class Automaton:
	def __init__(self,pos,shape,grid,flipped):
		self.drawAutomaton(pos,shape,grid,flipped)
		
	def drawAutomaton(self,sPos,shape,grid,flipped):
		for node in shape:
			pos = []
			for i in range(0,2):
				n = node[i]
				if flipped[i] and node[i] != None:
					n = not n		 
				if n:
					pos.append(sPos[i] + grid.tileSize[i] * node[i+2])
					if pos[i] >= grid.size[i]:
						pos[i] = pos[i] - grid.size[i]  
				elif n == False:
					pos.append(sPos[i] - grid.tileSize[i] * node[i+2])
					if pos[i] < 0:
						pos[i] = grid.size[i] + pos[i]
				else:
					pos.append(sPos[i])	
			grid.nodes[(pos[0],pos[1])].alive = True
			grid.nodes[(pos[0],pos[1])].color = (80,0,0)
			grid.liveNodes[(pos[0],pos[1])] = (pos[0],pos[1])
			grid.redrawNode(grid.nodes[(pos[0],pos[1])])
			
			
class Grid:
	def __init__(self,size,tileSize):
		self.surf = pygame.Surface(size)
		self.size = size
		self.tileSize = tileSize
		self.shape = None
		self.flip = (False,False)
		self.nodes = {}
		self.changedNodes = {}
		self.liveNodes = {}
		self.createGrid()
	
	def drawAutomaton(self,pos,shape):
		if shape == 'g':
			Automaton(pos,GLIDER,self,self.flip)
		elif shape == 'ge':
			Automaton(pos,GLIDEREMITTER,self,self.flip)
					
	def createGrid(self):
		for x in range(0,self.size[0],self.tileSize[0]):
			for y in range(0,self.size[1],self.tileSize[1]):
				self.nodes[(x,y)] = Node((x,y))	
						
	def toggleNode(self,node,liveNeighbors):
		if liveNeighbors != 2 and liveNeighbors != 3 and node.alive:
			self.changedNodes[node.pos] = False
		elif liveNeighbors == 3 and not node.alive:
			self.changedNodes[node.pos] = True
	
	def wrapAround(self,x,y):
		if x < 0:
			x = self.size[0] - self.tileSize[0]
		elif x >= self.size[0]:
			x = 0
		if y < 0:
			y = self.size[1] - self.tileSize[1]
		elif y >= self.size[1]:
			y = 0
		return x,y
	
	def checkDeadNode(self,pos):
		liveNeighbors = 0
		for x in range(pos[0] - self.tileSize[0],pos[0] + self.tileSize[0]*2,self.tileSize[0]):				
			for y in range(pos[1] - self.tileSize[1],pos[1] + self.tileSize[1]*2,self.tileSize[1]):
				if (x,y) != pos:					
					if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
						x,y = self.wrapAround(x,y)
					if self.nodes[(x,y)].alive:
						liveNeighbors += 1					
		self.toggleNode(self.nodes[pos],liveNeighbors)	
			
	def checkLiveNodes(self):
		checkedNodes = []
		for pos in self.liveNodes:
			liveNeighbors = 0
			for x in range(pos[0] - self.tileSize[0],pos[0] + self.tileSize[0]*2,self.tileSize[0]):				
				for y in range(pos[1] - self.tileSize[1],pos[1] + self.tileSize[1]*2,self.tileSize[1]):
					if (x,y) != pos:					
						if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
							x,y = self.wrapAround(x,y)
						if self.nodes[(x,y)].alive:
							liveNeighbors += 1
						if not self.nodes[(x,y)].alive and (x,y) not in checkedNodes:
							self.checkDeadNode((x,y))
							checkedNodes.append((x,y)) 
							self.nodes[(x,y)].color = self.nodes[pos].color			
			self.toggleNode(self.nodes[pos],liveNeighbors)	
	
	def changeNodes(self):
		for pos in self.changedNodes:
			self.nodes[pos].alive = self.changedNodes[pos]
			if not self.nodes[pos].alive:
				del self.liveNodes[pos]
			else:
				self.liveNodes[pos] = pos
			self.redrawNode(self.nodes[pos])
		self.changedNodes = {}
			
	def redrawNode(self,node):		
		if node.alive:
			pygame.draw.rect(self.surf,node.color,(node.pos,self.tileSize),0)
		else:
			pygame.draw.rect(self.surf,(0,0,0),(node.pos,self.tileSize),0)
	
	def clickNode(self,mInput,state):
		x = mInput[0] - (mInput[0] % self.tileSize[0]) 
		y = mInput[1] - (mInput[1] % self.tileSize[1]) 
		self.nodes[(x,y)].alive = state
		self.redrawNode(self.nodes[(x,y)])
		print("ORIGIN: ", x,y)
		if state:
			self.liveNodes[(x,y)] = (x,y)
			if self.shape != None:
				self.nodes[(x,y)].color = (80,0,0)			
				self.drawAutomaton((x,y),self.shape)
				
	def drawLines(self,windowSurf):
		for x in range(0,self.size[0],self.tileSize[0]):
			pygame.draw.line(windowSurf,(40,40,40),(x,0),(x,self.size[1]),1)
		for y in range(0,self.size[1],self.tileSize[1]):
			pygame.draw.line(windowSurf,(40,40,40),(0,y),(self.size[0],y),1)
						
	def update(self,paused):
		if not paused:
			self.checkLiveNodes()
			self.changeNodes()									
		
class Menu:
	def __init__(self,size,pos):
		self.pos = pos
		self.size = size
		self.surf = pygame.Surface(size)
		self.font1 = pygame.font.Font('freesansbold.ttf', 20)	
		self.statFontObjs = []
		
	def showOptions(self):
		pass
				
def test():
	pygame.init()
	fpsClock = pygame.time.Clock()
	
	pygame.display.set_caption("Game of Life")
	
	windowSize = (1200, 600)
	windowSurf = pygame.display.set_mode(windowSize)
	
	grid = Grid(GRIDSIZE,TILESIZE)
	
	paused = False
	
	click = False
	
	gridLines = True
	
	
	s = 0
	while True:	
		keysPressed = pygame.key.get_pressed()
		events = pygame.event.get()
		event = pygame.event.poll()
		mButtons = pygame.mouse.get_pressed()
		for event in events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()						
			if mButtons[0]:
				grid.clickNode(pygame.mouse.get_pos(),True)	
			if mButtons[2]:
				grid.clickNode(pygame.mouse.get_pos(),False)	
			if event.type == KEYDOWN:
				if event.key == K_UP:
					grid.flip = (grid.flip[0],True)
				if event.key == K_DOWN:
					grid.flip = (grid.flip[0],False)
				if event.key == K_LEFT:
					grid.flip = (True,grid.flip[1])
				if event.key == K_RIGHT:
					grid.flip = (False,grid.flip[1])
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()	
				if event.key == K_w:
					s += 1
					if s > len(SHAPES)-1:
						s = 0
					grid.shape = SHAPES[s]
				if event.key == K_q:
					s -= 1
					if s < 0:
						s = len(SHAPES)-1
					grid.shape = SHAPES[s]
				if event.key == K_p:
					if not paused:
						paused = True
						fps = 60
					else:
						paused = False
						fps = 20
				if event.key == K_g:
					gridLines = not gridLines
				if event.key == K_SPACE:
					return
					
		windowSurf.fill((255,255,255))
		
		grid.update(paused)
		
		windowSurf.blit(grid.surf,(0,0))
		if gridLines:
			grid.drawLines(windowSurf)
			
		pygame.display.flip()
		fpsClock.tick(FPS)
		
while True:
	test()		
