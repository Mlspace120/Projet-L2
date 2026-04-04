let canvasWidth = 1200; 
let canvasHeight = 700;

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
canvas.width = canvasWidth;
canvas.height = canvasHeight;

// UI Elements
const startScreen = document.getElementById('startScreen');
const gameArea = document.getElementById('gameArea');
const startBtn = document.getElementById('startBtn');
const playerNameInput = document.getElementById('playerName');
const highScoreDisplay = document.getElementById('highScoreDisplay');
const leaderboardList = document.getElementById('leaderboardList');
const uiPlayerName = document.getElementById('uiPlayerName');
const uiScore = document.getElementById('uiScore');

let gameStarted = false;
let playerName = "";
let score = 0;
let animationId = null;
let obstacleSpawnTimer = 0; // Déplacé ici pour éviter les bugs de scope
let groundScroll = 0; 

// --- GESTION DES IMAGES (Optimisée pour éviter le lag) ---
const bgSources = [
    "background/capitole.png",
    "background/cheztt.png", 
    "background/festival.png",
    "background/shop.png",
    "background/studio.png"
];

const backgrounds = bgSources.map(src => {
    let img = new Image();
    img.src = src;
    return img;
});

const groundImg = new Image();
groundImg.src = "background/briques.jpg";

const obstacleImg = new Image();
obstacleImg.src = "background/paparazzi.png";

const dinoFrames = ["personnage/1.png","personnage/2.png","personnage/3.png","personnage/4.png"]
    .map(src => { let img = new Image(); img.src = src; return img; });

let currentFrame = 0;
let frameTimer = 0;

// --- PHYSIQUE ET RÉGLAGES VISUELS ---
const groundHeight = 120; 
const groundLevel = canvasHeight - groundHeight; 

const offsetDino = 135;      
const offsetPaparazzi = 75;  

let dino = {
    x: 150,
    y: groundLevel,
    width: 360,
    height: 410,
    velocityY: 0,
    gravity: 0.5, 
    jumpPower: -17
};

let obstacles = [];
function spawnObstacle() {
    obstacles.push({
        x: canvas.width + 100,
        y: groundLevel,
        width: 240,
        height: 280
    });
}

// --- VARIABLES DU DÉFILEMENT ---
let bg1_x = 0;
let bg2_x = canvasWidth;
let currentBgIndex = 0;
let nextBgIndex = (backgrounds.length > 1) ? 1 : 0;

// CONTRÔLES
document.addEventListener("keydown", e => {
    if (!gameStarted) return;
    if ((e.code === "Space" || e.code === "ArrowUp") && dino.y >= groundLevel - 10) {
        dino.velocityY = dino.jumpPower;
    }
    if (e.code === "Escape") saveScoreAndStopGame();
});

// CLASSEMENT
function updateLeaderboardUI() {
    let board = JSON.parse(localStorage.getItem('dinoLeaderboard')) || [];
    leaderboardList.innerHTML = "";
    if (board.length === 0) {
        leaderboardList.innerHTML = "<li>Aucun score</li>";
        highScoreDisplay.innerText = "0";
    } else {
        board.forEach(entry => {
            let li = document.createElement('li');
            li.innerHTML = `${entry.name} <span>${entry.score}</span>`;
            leaderboardList.appendChild(li);
        });
        highScoreDisplay.innerText = board[0].score;
    }
}

function saveScoreAndStopGame() {
    gameStarted = false;
    cancelAnimationFrame(animationId);
    let finalScore = Math.floor(score);
    let board = JSON.parse(localStorage.getItem('dinoLeaderboard')) || [];
    board.push({ name: playerName, score: finalScore });
    board.sort((a, b) => b.score - a.score);
    board = board.slice(0, 5);
    localStorage.setItem('dinoLeaderboard', JSON.stringify(board));
    updateLeaderboardUI();
    gameArea.classList.add('hidden');
    startScreen.classList.remove('hidden');
}

// START
startBtn.addEventListener('click', () => {
    playerName = playerNameInput.value || "Joueur";
    score = 0;
    gameStarted = true;
    dino.y = groundLevel;
    dino.velocityY = 0;
    obstacles = [];
    bg1_x = 0;
    bg2_x = canvasWidth;
    currentBgIndex = 0;
    nextBgIndex = (backgrounds.length > 1) ? 1 : 0;
    uiPlayerName.innerText = playerName;
    uiScore.innerText = "Score : 0";
    startScreen.classList.add('hidden');
    gameArea.classList.remove('hidden');
    update();
});

// --- GAME LOOP ---
function update() {
    if (!gameStarted) return;
    score += 0.05;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. DÉFILEMENT BACKGROUNDS
    bg1_x -= 1.5; 
    bg2_x -= 1.5;
    if (bg1_x <= -canvasWidth) {
        bg1_x = bg2_x + canvasWidth;
        currentBgIndex = (nextBgIndex + 1) % backgrounds.length;
    }
    if (bg2_x <= -canvasWidth) {
        bg2_x = bg1_x + canvasWidth;
        nextBgIndex = (currentBgIndex + 1) % backgrounds.length;
    }
    ctx.drawImage(backgrounds[currentBgIndex], bg1_x, 0, canvasWidth, canvasHeight);
    ctx.drawImage(backgrounds[nextBgIndex], bg2_x, 0, canvasWidth, canvasHeight);

    // 2. PHYSIQUE DINO
    dino.velocityY += dino.gravity;
    dino.y += dino.velocityY;
    if (dino.y > groundLevel) {
        dino.y = groundLevel;
        dino.velocityY = 0;
    }

    // --- HITBOX DINO ---
    let dMarginL = 130; 
    let dMarginR = 130; 
    let dMarginT = 110; 
    let dMarginB = 90;  

    let dinoHitbox = {
        left: dino.x + dMarginL,
        right: dino.x + dino.width - dMarginR,
        top: (dino.y - dino.height + offsetDino) + dMarginT,
        bottom: (dino.y + offsetDino) - dMarginB
    };

    // 3. OBSTACLES
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= 5; 
        
        // Dessin de l'obstacle
        ctx.drawImage(obstacleImg, obs.x, obs.y - obs.height + offsetPaparazzi, obs.width, obs.height);

        // --- HITBOX OBSTACLE ---
        let oMarginL = 65;  
        let oMarginR = 110; 
        let oMarginT = 95;  
        let oMarginB = 20;  

        let obsHitbox = {
            left: obs.x + oMarginL,
            right: obs.x + obs.width - oMarginR,
            top: (obs.y - obs.height + offsetPaparazzi) + oMarginT,
            bottom: (obs.y + offsetPaparazzi) - oMarginB
        };

        // DESSIN HITBOX OBSTACLE (ROUGE) - À commenter à la fin
        // ctx.strokeStyle = "red";
        // ctx.strokeRect(obsHitbox.left, obsHitbox.top, obsHitbox.right - obsHitbox.left, obsHitbox.bottom - obsHitbox.top);

        // COLLISION
        if (dinoHitbox.right > obsHitbox.left && 
            dinoHitbox.left < obsHitbox.right && 
            dinoHitbox.bottom > obsHitbox.top && 
            dinoHitbox.top < obsHitbox.bottom) {
            saveScoreAndStopGame();
        }

        if (obs.x + obs.width < 0) obstacles.splice(i, 1);
    }

    // 4. PERSONNAGE
    frameTimer++;
    if (frameTimer > 12) { 
        currentFrame = (currentFrame + 1) % dinoFrames.length;
        frameTimer = 0;
    }
    ctx.drawImage(dinoFrames[currentFrame], dino.x, dino.y - dino.height + offsetDino, dino.width, dino.height);

    // DESSIN HITBOX DINO (VERT) - À commenter à la fin
    // ctx.strokeStyle = "lime";
    // ctx.strokeRect(dinoHitbox.left, dinoHitbox.top, dinoHitbox.right - dinoHitbox.left, dinoHitbox.bottom - dinoHitbox.top);

    
    // 5. SOL (Rendu propre et défilement infini)
    const imgRatio = groundImg.naturalWidth / groundImg.naturalHeight || 1;
    const drawWidth = groundHeight * imgRatio;

    // On fait défiler le sol à la même vitesse que les obstacles
    groundScroll -= 4; 

    // Le modulo (%) permet de garder la valeur entre 0 et -drawWidth
    // On ajoute drawWidth pour être sûr de ne jamais avoir de trou à gauche
    let groundX = groundScroll % drawWidth;

    // On dessine assez de briques pour couvrir toute la largeur + une de sécurité
    for (let x = groundX; x < canvas.width + drawWidth; x += drawWidth) {
        ctx.drawImage(groundImg, x, groundLevel, drawWidth, groundHeight);
    }
    // SPAWN
    obstacleSpawnTimer++;
    if (obstacleSpawnTimer > 130) {
        if (Math.random() < 0.5) spawnObstacle();
        obstacleSpawnTimer = 0;
    }

    uiScore.innerText = "Score : " + Math.floor(score);
    animationId = requestAnimationFrame(update);
}

// Initialisation
updateLeaderboardUI();