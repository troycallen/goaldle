export interface Player {
  id: string;
  name: string;
  team: string;
  position: string;
  nationality: string;
  age: number;
  height: number; // in cm
  jerseyNumber?: number;
  media: {
    type: 'image' | 'video';
    url: string;
    thumbnail?: string;
    description: string;
  };
  hints: string[];
}

// Curated player database with daily challenges
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
    media: {
      type: 'image',
      url: 'https://via.placeholder.com/400x400/ff0000/ffffff?text=MESSI',
      description: 'Test image for Lionel Messi'
    },
    hints: [
      'This player has won 8 Ballon d\'Or awards',
      'Known as "La Pulga" (The Flea)',
      'Currently plays in MLS',
      'Led Argentina to World Cup victory in 2022'
    ]
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
    media: {
      type: 'image',
      url: '/players/ronaldo.svg',
      description: 'Cristiano Ronaldo celebrating'
    },
    hints: [
      'All-time top scorer in Champions League',
      'Known as "CR7"',
      'Has played in England, Spain, Italy, and Saudi Arabia',
      'Won Euro 2016 with his national team'
    ]
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
    media: {
      type: 'image',
      url: '/players/mbappe.svg',
      description: 'Kylian Mbappé in action'
    },
    hints: [
      'World Cup winner at age 19',
      'One of the fastest players in world football',
      'Recently transferred to Real Madrid',
      'Became PSG\'s all-time leading scorer'
    ]
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
    media: {
      type: 'image',
      url: '/players/haaland.svg',
      description: 'Erling Haaland in Manchester City colors'
    },
    hints: [
      'Scored 52 goals in his debut Premier League season',
      'Son of former player Alfie Haaland',
      'Known for his incredible finishing ability',
      'Helped Manchester City win the treble'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Neymar showing his skills'
    },
    hints: [
      'Most expensive transfer in football history',
      'Known for his flair and skill moves',
      'Olympic gold medalist with Brazil',
      'Former Barcelona and PSG star'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Kevin De Bruyne creating a play'
    },
    hints: [
      'One of the best playmakers in the world',
      'Known for his incredible passing range',
      'Multiple Premier League champion',
      'PFA Player of the Year winner'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Mohamed Salah on the attack'
    },
    hints: [
      'Known as the "Egyptian King"',
      'Premier League Golden Boot winner',
      'Champions League winner with Liverpool',
      'First Arab player to score 150+ Premier League goals'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Virgil van Dijk defending'
    },
    hints: [
      'Most expensive defender in football history (at time of transfer)',
      'Champions League and Premier League winner',
      'Known for his aerial ability and leadership',
      'Netherlands national team captain'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Luka Modrić controlling the midfield'
    },
    hints: [
      'Ballon d\'Or winner in 2018',
      'Led Croatia to World Cup final',
      'Multiple Champions League winner',
      'Known for his incredible longevity'
    ]
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
    media: {
      type: 'image',
      url: '/players/default.svg',
      description: 'Harry Kane taking a shot'
    },
    hints: [
      'England\'s all-time leading goalscorer',
      'Multiple Premier League Golden Boot winner',
      'Recently transferred to Bayern Munich',
      'Known for his clinical finishing'
    ]
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

  getPlayerHints(player: Player, attemptNumber: number): string[] {
    // Reveal hints progressively based on attempt number
    return player.hints.slice(0, Math.min(attemptNumber, player.hints.length));
  }
}

export const playerDB = new PlayerDatabase();