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

    def GetDistances( self, to, fr = None ):
        targets = []
        distances = []
        if fr == None:
            fr = self.data[ self.ownerName ][ "adjacent" ][ "all" ]
        for target in fr:
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
            return self.AttackTargets( targets, distances = True )

    def PursueGold( self ):
        if len( self.data[ "empty" ][ "gold" ] ) > 0:
            targets = self.GetDistances( self.data[ "empty" ][ "gold" ] )
            targets.sort( key = lambda tup: tup[ 1 ] )
            return self.AttackTargets( targets, distances = True )
        if len( self.data[ "enemy" ][ "gold" ] ) > 0:
            targets = self.GetDistances( self.data[ "enemy" ][ "gold" ] )
            targets.sort( key = lambda tup: tup[ 1 ] )
            return self.AttackTargets( targets, distances = True )

    def PursueFast( self ):
        self.data[ self.ownerName ][ "adjacent" ][ "all" ].sort( key = lambda cell: int( cell.takeTime * 10 ) )
        return self.AttackTargets( self.data[ self.ownerName ][ "adjacent" ][ "all" ] )        

    def Start( self ):
        self.game.Refresh()
        while self.data[ "playing" ]:
            if self.data[ "debug" ]:
                self.GameLoop()
            else:
                try:
                    self.GameLoop()
                except:
                    pass           

    def GetDamage( self, cell ):
        if not cell:
            return 0
        if cell.owner in self.data[ "holders" ] or cell.owner == 0:
            if cell.owner == self.data[ "leader" ] and self.game.uid != self.data[ "leader" ]:
                return -1
            else:
                return 0
        else:
            if cell.cellType == "gold":
                return 10
            else:
                return 1

    def GetHDamage( self, cell ):
        damage = 0
        for xx in range( -4, 5 ):
            if not xx == 0:
                dmg = self.GetDamage( self.data[ "master" ].GetCell( cell.x + xx, cell.y ) )
                if dmg == -1:
                    return -1
                damage += dmg
        return damage

    def GetVDamage( self, cell ):
        damage = 0
        for yy in range( -4, 5 ):
            if not yy == 0:
                dmg = self.GetDamage( self.data[ "master" ].GetCell( cell.x, cell.y + yy ) )
                if dmg == -1:
                    return -1
                damage += dmg
        return damage

    def GetSDamage( self, cell ):
        damage = 0
        for xx in range( -1, 2 ):
            for yy in range( -1, 2 ):
                if not ( xx == 0 and yy == 0 ):
                    dmg = self.GetDamage( self.data[ "master" ].GetCell( cell.x + xx, cell.y + yy ) )
                    if dmg == -1:
                        return -1
                    damage += dmg
        return damage

    def EvaluateCataclysm( self ):
        damages = []
        for cell in self.data[ self.ownerName ][ "own" ][ "all" ]:
            damages.append( ( cell, self.GetHDamage( cell ), "horizontal" ) )
            damages.append( ( cell, self.GetVDamage( cell ), "vertical" ) )
            damages.append( ( cell, self.GetSDamage( cell ), "square" ) )
        damages.sort( key = lambda tup: tup[ 1 ], reverse = True )
        return damages

    def Cataclysm( self ):
        damages = self.EvaluateCataclysm()
        for target in damages:
            if target[ 1 ] > 0:
                self.game.Blast( target[ 0 ].x, target[ 0 ].y, target[ 2 ] )


    def ProtectEiffel( self ):
        targets = self.GetDistances( self.data[ self.ownerName ][ "own" ][ "safebases" ] )
        targets.sort( key = lambda tup: tup[ 1 ] )
        return self.AttackTargets( targets, distances = True )

    def BuildEiffel( self ):
        if len( self.data[ self.ownerName ][ "own" ][ "safe" ] ) > 0:
            if len( self.data[ "enemy" ][ "all" ] ) > 0:
                targets = self.GetDistances( self.data[ "enemy" ][ "all" ], self.data[ self.ownerName ][ "own" ][ "safe" ] )
                targets.sort( key = lambda tup: tup[ 1 ], reverse = True )
                for target in targets:
                    self.game.BuildBase( target[ 0 ].x, target[ 0 ].y )
        else:
            if self.game.baseNum == 2:
                if len( self.data[ "enemy" ][ "all" ] ) > 0:
                    targets = self.GetDistances( self.data[ "enemy" ][ "all" ], self.data[ self.ownerName ][ "own" ][ "all" ] )
                    targets.sort( key = lambda tup: tup[ 1 ], reverse = True )
                    for target in targets:
                        self.game.BuildBase( target[ 0 ].x, target[ 0 ].y )

    def GameLoop( self ):
        if self.game.baseNum < 3 and self.game.gold >= 60:
            self.BuildEiffel()
        if self.game.endTime == 0 or self.data[ "time" ] < self.game.endTime - 5:
            if len( self.data[ self.ownerName ][ "own" ][ "safe" ] ) == 0 and choice( ( 0, 1 ) ) == 0:
                return self.PursueSafe()
            else:
                if( self.game.goldCellNum == 0 and self.game.baseNum < 2 ):
                    return self.PursueGold()
                else:
                    if len( self.data[ self.ownerName ][ "own" ][ "safebases" ] ) > 0:
                        self.ProtectEiffel()
                    else:
                        self.PursueFast()
        else:
            self.Cataclysm()


class MasterFu:
    def __init__( self ):
        # Initialize the Refresh loop
        self.info = Game()

        # Initialize the hive mind
        self.data = {}
        self.data[ "playing" ] = True
        self.data[ "debug" ] = False
        self.data[ "ids" ] = {}
        self.data[ "master" ] = self.info

        # Initialize the Miraculous holders
        self.mari = Kwami( "Tikki", "Marinette", self.data )
        self.adrien = Kwami( "Plagg", "Adrien", self.data )
        self.alya = Kwami( "Trixx", "Alya", self.data )

        # Initialize Wayzz's communication
        self.wayzz = {}
        self.wayzz[ "Marinette" ] = self.mari
        self.wayzz[ "Adrien" ] = self.adrien
        self.wayzz[ "Alya" ] = self.alya

        # Transform the Miraculous holders
        self.holders = set()
        self.data[ "holders" ] = self.holders
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
                    if adj.isBase:
                        self.data[ self.data[ "ids" ][ adj.owner ] ][ "own" ][ "safebases" ].append( adj )

    def Refresh( self ):
        self.info.Refresh()
        self.data[ "time" ] = self.info.currTime
        self.data[ "leader" ] = self.mari.game.uid
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
            self.data[ ownerName ][ "own" ][ "safebases" ] = []
        for t in ( "empty", "enemy" ):
            self.data[ t ] = {}
            self.data[ t ][ "all" ] = []
            self.data[ t ][ "gold" ] = []
            self.data[ t ][ "energy" ] = []
            self.data[ t ][ "normal" ] = []
        leader = []
        for user in self.info.users:
            if user.id in self.holders:
                s = self.wayzz[ self.data[ "ids" ][ user.id ] ].game
                s.gold   = user.gold
                s.energy = user.energy
                s.cdTime = user.cdTime
                s.buildCdTime = user.buildCdTime
                s.cellNum = user.cellNum
                s.baseNum = user.baseNum
                s.goldCellNum = user.goldCellNum
                s.energyCellNum = user.energyCellNum
                leader.append( ( user.id, s.cellNum ) )
        leader.sort( key = lambda tup: tup[ 1 ], reverse = True )
        if len( leader ) > 0:
            self.data[ "leader" ] = leader[ 0 ][ 0 ]
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