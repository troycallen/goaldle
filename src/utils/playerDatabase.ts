export interface Player {
  id: string;
  name: string;
  team: string;
  position: string;
  nationality: string;
  age: number;
  height: number; // in cm
  imageUrl?: string;
  jerseyNumber?: number;
  features: {
    hair_color: string;
    skin_tone: string;
    height_category: 'short' | 'medium' | 'tall';
    jersey_colors: string[];
  };
}

// Mock player database - in production, this would come from a real database
export const PLAYERS: Player[] = [
  {
    id: '1',
    name: 'Lionel Messi',
    team: 'Inter Miami',
    position: 'Forward',
    nationality: 'Argentina',
    age: 36,
    height: 170,
    jerseyNumber: 10,
    features: {
      hair_color: 'brown',
      skin_tone: 'light',
      height_category: 'short',
      jersey_colors: ['pink', 'white', 'blue']
    }
  },
  {
    id: '2',
    name: 'Cristiano Ronaldo',
    team: 'Al Nassr',
    position: 'Forward',
    nationality: 'Portugal',
    age: 39,
    height: 187,
    jerseyNumber: 7,
    features: {
      hair_color: 'black',
      skin_tone: 'medium',
      height_category: 'tall',
      jersey_colors: ['yellow', 'blue', 'white']
    }
  },
  {
    id: '3',
    name: 'Kylian Mbappé',
    team: 'Real Madrid',
    position: 'Forward',
    nationality: 'France',
    age: 25,
    height: 178,
    jerseyNumber: 9,
    features: {
      hair_color: 'black',
      skin_tone: 'dark',
      height_category: 'medium',
      jersey_colors: ['white', 'blue', 'red']
    }
  },
  {
    id: '4',
    name: 'Erling Haaland',
    team: 'Manchester City',
    position: 'Forward',
    nationality: 'Norway',
    age: 24,
    height: 194,
    jerseyNumber: 9,
    features: {
      hair_color: 'blonde',
      skin_tone: 'light',
      height_category: 'tall',
      jersey_colors: ['sky_blue', 'white', 'navy']
    }
  },
  {
    id: '5',
    name: 'Neymar Jr',
    team: 'Al Hilal',
    position: 'Forward',
    nationality: 'Brazil',
    age: 32,
    height: 175,
    jerseyNumber: 10,
    features: {
      hair_color: 'blonde',
      skin_tone: 'medium',
      height_category: 'medium',
      jersey_colors: ['blue', 'white', 'yellow']
    }
  },
  {
    id: '6',
    name: 'Kevin De Bruyne',
    team: 'Manchester City',
    position: 'Midfielder',
    nationality: 'Belgium',
    age: 33,
    height: 181,
    jerseyNumber: 17,
    features: {
      hair_color: 'blonde',
      skin_tone: 'light',
      height_category: 'medium',
      jersey_colors: ['sky_blue', 'white', 'red']
    }
  },
  {
    id: '7',
    name: 'Mohamed Salah',
    team: 'Liverpool',
    position: 'Forward',
    nationality: 'Egypt',
    age: 32,
    height: 175,
    jerseyNumber: 11,
    features: {
      hair_color: 'black',
      skin_tone: 'medium',
      height_category: 'medium',
      jersey_colors: ['red', 'white', 'yellow']
    }
  },
  {
    id: '8',
    name: 'Virgil van Dijk',
    team: 'Liverpool',
    position: 'Defender',
    nationality: 'Netherlands',
    age: 33,
    height: 193,
    jerseyNumber: 4,
    features: {
      hair_color: 'black',
      skin_tone: 'dark',
      height_category: 'tall',
      jersey_colors: ['red', 'white', 'orange']
    }
  },
  {
    id: '9',
    name: 'Luka Modrić',
    team: 'Real Madrid',
    position: 'Midfielder',
    nationality: 'Croatia',
    age: 39,
    height: 172,
    jerseyNumber: 10,
    features: {
      hair_color: 'brown',
      skin_tone: 'light',
      height_category: 'short',
      jersey_colors: ['white', 'navy', 'red']
    }
  },
  {
    id: '10',
    name: 'Harry Kane',
    team: 'Bayern Munich',
    position: 'Forward',
    nationality: 'England',
    age: 31,
    height: 188,
    jerseyNumber: 9,
    features: {
      hair_color: 'brown',
      skin_tone: 'light',
      height_category: 'tall',
      jersey_colors: ['red', 'white', 'navy']
    }
  }
];

export class PlayerDatabase {
  private players: Player[] = PLAYERS;

  getAllPlayers(): Player[] {
    return this.players;
  }

  getPlayerByName(name: string): Player | undefined {
    return this.players.find(player => 
      player.name.toLowerCase() === name.toLowerCase()
    );
  }

  searchPlayers(query: string): Player[] {
    const lowercaseQuery = query.toLowerCase();
    return this.players.filter(player =>
      player.name.toLowerCase().includes(lowercaseQuery) ||
      player.team.toLowerCase().includes(lowercaseQuery) ||
      player.nationality.toLowerCase().includes(lowercaseQuery)
    );
  }

  getRandomPlayer(): Player {
    const randomIndex = Math.floor(Math.random() * this.players.length);
    return this.players[randomIndex];
  }

  getDailyPlayer(date: Date = new Date()): Player {
    // Generate consistent daily player based on date
    const dateString = date.toISOString().split('T')[0];
    const hash = this.simpleHash(dateString);
    const index = hash % this.players.length;
    return this.players[index];
  }

  private simpleHash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  getPlayersSimilarTo(targetPlayer: Player, features: { jersey_color?: string; estimated_height?: string; hair_color?: string }): Player[] {
    return this.players.filter(player => {
      if (player.id === targetPlayer.id) return false;
      
      let similarityScore = 0;
      
      // Check jersey color match
      if (features.jersey_color && 
          player.features.jersey_colors.includes(features.jersey_color)) {
        similarityScore++;
      }
      
      // Check height category match
      if (features.estimated_height === player.features.height_category) {
        similarityScore++;
      }
      
      // Check hair color match
      if (features.hair_color === player.features.hair_color) {
        similarityScore++;
      }
      
      return similarityScore > 0;
    });
  }
}

export const playerDB = new PlayerDatabase();