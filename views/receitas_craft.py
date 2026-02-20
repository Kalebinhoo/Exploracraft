
RECEITAS_CRAFT = {
	"Tábua de Carvalho": {"Tronco de Carvalho": 1},
	"Tábua de Abeto": {"Tronco de Abeto": 1},
	"Tábua de Acácia": {"Tronco de Acácia": 1},
	"Tábua de Bétula": {"Tronco de Bétula": 1},
	"Tábua de Carvalho Escuro": {"Tronco de Carvalho Escuro": 1},
	"Tábua de Cerejeira": {"Tronco de Cerejeira": 1},
	"Tábua de Selva": {"Tronco de Selva": 1},
	"Tábua de Mangue": {"Tronco de Mangue": 1},
	"Graveto": {"Tábua de Carvalho": 2},

	"Madeira": {"Tábua de Carvalho": 4},
	"Fornalha": {"Pedregulho": 8},
	"Cama": {"Tábua de Carvalho": 3, "Lã": 3},  
	"Pá de Madeira": {"Graveto": 2, "Tábua de Carvalho": 1},
	"Pá de Pedra": {"Graveto": 2, "Pedregulho": 1},
	"Pá de Ferro": {"Graveto": 2, "barradeferro": 1},
	"Machado de Madeira": {"Graveto": 3, "Tábua de Carvalho": 2},
	"Machado de Pedra": {"Graveto": 3, "Pedregulho": 2},
	"Machado de Ferro": {"Graveto": 3, "barradeferro": 2},
	"Picareta de Madeira": {"Graveto": 2, "Tábua de Carvalho": 3},
	"Picareta de Pedra": {"Graveto": 2, "Pedregulho": 3},
	"Picareta de Ferro": {"Graveto": 2, "barradeferro": 3},
	"Picareta de Ouro": {"Graveto": 2, "barradeouro": 3},
	"Picareta de Diamante": {"Graveto": 2, "diamante": 3},
	"Enxada de Madeira": {"Graveto": 2, "Tábua de Carvalho": 2},
	"Enxada de Pedra": {"Graveto": 2, "Pedregulho": 2},
	"Enxada de Ferro": {"Graveto": 2, "barradeferro": 2},
	"Espada de Madeira": {"Graveto": 2, "Tábua de Carvalho": 1},
	"Espada de Pedra": {"Graveto": 2, "Pedregulho": 1},
	"Espada de Ferro": {"Graveto": 2, "barradeferro": 1},
}

def pode_craftar(item):
	"""Verifica se o item pode ser craftado."""
	return item in RECEITAS_CRAFT

def get_receita(item):
	"""Retorna os ingredientes necessários para craftar o item."""
	return RECEITAS_CRAFT.get(item, None)
