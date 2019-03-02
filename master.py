# You need to import colorfight for all the APIs
from colorfight import Game, User, Cell
from random import shuffle, choice
from threading import Thread
        
try:
    input = raw_input
except NameError:
    pass

class Kwami:
    def __init__( self, kwamiName, ownerName, data ):
        self.data = data
        self.kwamiName = kwamiName
        self.ownerName = ownerName
        self.game = Game()
    
    def Transform( self, name ):
        print( self.ownerName + ": " + self.kwamiName + ", transform me!" )  
        if self.game.JoinGame( name ):
            print( self.ownerName + " transformed!\n" )
            return self.game.uid
        else:
            print( self.kwamiName + " is too tired.\n" )
            return 0

    def Attack( self, cell ):
        if cell.owner != self.game.uid and 0 < cell.takeTime < 4.0 and not cell.isTaking:
            data = self.game.AttackCell( cell.x, cell.y )
            while( data[ 1 ] == 3 ):
                data = self.game.AttackCell( cell.x, cell.y )
            return data[ 0 ]
        return False

    def AttackTargets( self, targets, distances = False ):
        for target in targets:
            if distances:
                target = target[ 0 ]
            if self.Attack( target ):
                return

    def GetDistance( self, c1, c2 ):
        return ( c1.y - c2.y ) ** 2 + ( c1.x - c2.x ) ** 2

    def GetDistances( self, to ):
        targets = []
        distances = []
        for target in self.data[ self.ownerName ][ "adjacent" ][ "all" ]:
            distances = []
            for gold in to:
                distances.append( self.GetDistance( target, gold ) )
            distances.sort()
            targets.append( ( target, distances[ 0 ] ) )
        return targets
        
    def PursueSafe( self ):
        allies = []
        for ally in self.data[ self.ownerName ][ "allies" ]:
            allies += self.data[ ally ][ "own" ][ "all" ]
        if len( allies ) > 0:
            targets = self.GetDistances( allies )
            targets.sort( key = lambda tup: tup[ 1 ] )
            self.AttackTargets( targets, distances = True )

    def PursueGold( self ):
        if len( self.data[ "empty" ][ "gold" ] ) > 0:
            targets = self.GetDistances( self.data[ "empty" ][ "gold" ] )
            targets.sort( key = lambda tup: tup[ 1 ] )
            self.AttackTargets( targets, distances = True )
        if len( self.data[ "enemy" ][ "gold" ] ) > 0:
            targets = self.GetDistances( self.data[ "enemy" ][ "gold" ] )
            targets.sort( key = lambda tup: tup[ 1 ] )
            self.AttackTargets( targets, distances = True )

    def Start( self ):
        while self.data[ "playing" ]:
            if self.data[ "debug" ]:
                self.GameLoop()
            else:
                try:
                    self.GameLoop()
                except:
                    pass           

    def GameLoop( self ):
        if len( self.data)
        if choice( ( 0, 1 ) ) == 0:
            self.PursueGold()
        else:
            self.PursueSafe()

class MasterFu:
    def __init__( self ):
        # Initialize the Refresh loop
        self.info = Game()

        # Initialize the hive mind
        self.data = {}
        self.data[ "playing" ] = True
        self.data[ "debug" ] = True
        self.data[ "ids" ] = {}

        # Initialize the Miraculous holders
        self.mari = Kwami( "Tikki", "Marinette", self.data )
        self.adrien = Kwami( "Plagg", "Adrien", self.data )
        self.alya = Kwami( "Trixx", "Alya", self.data )

        # Transform the Miraculous holders
        self.holders = set()
        self.mari.Transform( "THS Mari" )
        self.adrien.Transform( "THS Adrien" )
        self.alya.Transform( "THS Alya" )
        self.data[ "ids" ][ self.mari.game.uid ] = "Marinette"
        self.data[ "ids" ][ self.adrien.game.uid ] = "Adrien"
        self.data[ "ids" ][ self.alya.game.uid ] = "Alya"
        self.holders.add( self.mari.game.uid )
        self.holders.add( self.adrien.game.uid )
        self.holders.add( self.alya.game.uid )

        # Populate the hive mind
        self.Refresh()

        # Transform Master Fu
        self.Transform()

    def OwnCell( self, cell ):
        return cell.owner in self.holders

    def GetAdjacent( self, cell ):
        up = self.info.GetCell( cell.x, cell.y - 1 )
        right = self.info.GetCell( cell.x + 1, cell.y )
        down = self.info.GetCell( cell.x, cell.y + 1 )
        left = self.info.GetCell( cell.x - 1, cell.y )
        return ( up, right, down, left )

    def EvaluateCell( self, cell ):
        ownerName = self.data[ "ids" ][ cell.owner ]
        self.data[ ownerName ][ "own" ][ "all" ].append( cell )
        for adj in self.GetAdjacent( cell ):
            if adj:
                if not self.OwnCell( adj ):
                    self.data[ ownerName ][ "adjacent" ][ "all" ].append( adj )
                elif not adj.owner == cell.owner:
                    self.data[ self.data[ "ids" ][ adj.owner ] ][ "own" ][ "safe" ].append( adj )

    def Refresh( self ):
        self.info.Refresh()
        self.data[ "Marinette" ] = {}
        self.data[ "Marinette" ][ "allies" ] = [ "Adrien", "Alya" ]
        self.data[ "Adrien" ] = {}
        self.data[ "Adrien" ][ "allies" ] = [ "Marinette", "Alya" ]
        self.data[ "Alya" ] = {}
        self.data[ "Alya" ][ "allies" ] = [ "Adrien", "Marinette" ]
        for ownerName in ( "Marinette", "Adrien", "Alya" ):
            for t in ( "own", "adjacent" ):
                self.data[ ownerName ][ t ] = {}
                for s in ( "all", "bases" ):
                    self.data[ ownerName ][ t ][ s ] = []
                self.data[ ownerName ][ "own" ][ "safe" ] = []
        for t in ( "empty", "enemy" ):
            self.data[ t ] = {}
            self.data[ t ][ "all" ] = []
            self.data[ t ][ "gold" ] = []
            self.data[ t ][ "energy" ] = []
            self.data[ t ][ "normal" ] = []
        for x in range( 30 ):
            for y in range( 30 ):
                c = self.info.GetCell( x, y )
                if self.OwnCell( c ):
                    self.EvaluateCell( c )
                else:
                    if c.owner == 0:
                        self.data[ "empty" ][ "all" ].append( c )
                        self.data[ "empty" ][ c.cellType ].append( c )
                    else:
                        self.data[ "enemy" ][ "all" ].append( c )
                        self.data[ "enemy" ][ c.cellType ].append( c )

    def GameLoop( self ):
        while self.data[ "playing" ]:
            self.Refresh()

    def Transform( self ):
        mariThread = Thread( target = self.mari.Start )
        adrienThread = Thread( target = self.adrien.Start )
        alyaThread = Thread( target = self.alya.Start )
        fuThread = Thread( target = self.GameLoop )
        mariThread.start()
        adrienThread.start()
        alyaThread.start()
        fuThread.start()
        print( "Master Fu: Wayzz, transform me!" )
        print( "Master Fu transformed!" )
        while self.data[ "playing" ]:
            s = input()
            self.data[ "playing" ] = False

masterFu = MasterFu()