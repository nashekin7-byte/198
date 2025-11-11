// Windows 98 Desktop Shell - JavaScript

// Start Menu
class StartMenu {
    constructor() {
        this.startButton = document.querySelector('.start-button');
        this.menuContainer = document.querySelector('.start-menu-container');
        this.init();
    }

    init() {
        this.startButton.addEventListener('click', () => this.toggle());
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }

    toggle() {
        this.menuContainer.classList.toggle('active');
    }

    close() {
        this.menuContainer.classList.remove('active');
    }

    handleOutsideClick(e) {
        if (!e.target.closest('.start-button') && !e.target.closest('.start-menu-container')) {
            this.close();
        }
    }
}

// Desktop Icons
class DesktopIcon {
    constructor(element) {
        this.element = element;
        this.isSelected = false;
        this.init();
    }

    init() {
        this.element.addEventListener('click', () => this.select());
        this.element.addEventListener('dblclick', () => this.open());
    }

    select() {
        // Deselect all icons
        document.querySelectorAll('.icon').forEach(icon => {
            icon.classList.remove('selected');
        });
        this.element.classList.add('selected');
        this.isSelected = true;
    }

    open() {
        const label = this.element.querySelector('.icon-label').textContent;
        console.log(`Opening: ${label}`);
        // This would open a window or perform an action
        alert(`Opening: ${label}`);
    }
}

// Window Management
class Window {
    constructor(element) {
        this.element = element;
        this.isDragging = false;
        this.dragOffsetX = 0;
        this.dragOffsetY = 0;
        this.init();
    }

    init() {
        const titleBar = this.element.querySelector('.title-bar');
        if (titleBar) {
            titleBar.addEventListener('mousedown', (e) => this.startDrag(e));
        }

        const closeBtn = this.element.querySelector('.title-bar-button:nth-child(3)');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        const minimizeBtn = this.element.querySelector('.title-bar-button:nth-child(1)');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', () => this.minimize());
        }

        const maximizeBtn = this.element.querySelector('.title-bar-button:nth-child(2)');
        if (maximizeBtn) {
            maximizeBtn.addEventListener('click', () => this.maximize());
        }
    }

    startDrag(e) {
        if (e.target.closest('.title-bar-button')) return;
        
        this.isDragging = true;
        const rect = this.element.getBoundingClientRect();
        this.dragOffsetX = e.clientX - rect.left;
        this.dragOffsetY = e.clientY - rect.top;

        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('mouseup', () => this.stopDrag());
    }

    drag(e) {
        if (!this.isDragging) return;
        
        const x = e.clientX - this.dragOffsetX;
        const y = e.clientY - this.dragOffsetY;

        this.element.style.position = 'fixed';
        this.element.style.left = x + 'px';
        this.element.style.top = y + 'px';
        this.element.style.margin = '0';
        this.element.style.maxWidth = 'none';
        this.element.style.width = this.element.offsetWidth + 'px';
    }

    stopDrag() {
        this.isDragging = false;
        document.removeEventListener('mousemove', (e) => this.drag(e));
    }

    close() {
        this.element.style.display = 'none';
    }

    minimize() {
        alert('Window minimized! (stub)');
    }

    maximize() {
        if (this.element.style.maxWidth === '100%') {
            this.element.style.maxWidth = '';
        } else {
            this.element.style.maxWidth = '100%';
        }
    }
}

// Minesweeper Game
class Minesweeper {
    constructor() {
        this.gridElement = document.querySelector('.minesweeper-grid');
        this.counterElement = document.querySelector('.minesweeper-counter');
        this.smileyElement = document.querySelector('.minesweeper-smiley');
        this.gridSize = 10;
        this.mineCount = 10;
        this.grid = [];
        this.revealed = [];
        this.flagged = [];
        this.gameOver = false;
        this.init();
    }

    init() {
        if (!this.gridElement) return;
        
        this.initializeGrid();
        this.renderGrid();
        this.updateCounter();
        
        if (this.smileyElement) {
            this.smileyElement.addEventListener('click', () => this.reset());
        }
    }

    initializeGrid() {
        // Initialize empty grid
        this.grid = Array(this.gridSize * this.gridSize).fill(0);
        this.revealed = Array(this.gridSize * this.gridSize).fill(false);
        this.flagged = Array(this.gridSize * this.gridSize).fill(false);

        // Place mines randomly
        let minesPlaced = 0;
        while (minesPlaced < this.mineCount) {
            const idx = Math.floor(Math.random() * this.grid.length);
            if (this.grid[idx] !== 'M') {
                this.grid[idx] = 'M';
                minesPlaced++;
            }
        }

        // Calculate numbers
        for (let i = 0; i < this.grid.length; i++) {
            if (this.grid[i] === 'M') continue;
            
            let count = 0;
            const row = Math.floor(i / this.gridSize);
            const col = i % this.gridSize;

            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    const nr = row + dr;
                    const nc = col + dc;
                    if (nr >= 0 && nr < this.gridSize && nc >= 0 && nc < this.gridSize) {
                        const idx = nr * this.gridSize + nc;
                        if (this.grid[idx] === 'M') count++;
                    }
                }
            }
            
            if (count > 0) this.grid[i] = count;
        }

        this.gameOver = false;
    }

    renderGrid() {
        this.gridElement.innerHTML = '';
        
        for (let i = 0; i < this.grid.length; i++) {
            const cell = document.createElement('div');
            cell.className = 'mine-cell';
            
            if (this.revealed[i]) {
                cell.classList.add('revealed');
                if (this.grid[i] === 'M') {
                    cell.textContent = '💣';
                } else if (this.grid[i] > 0) {
                    cell.textContent = this.grid[i];
                }
            } else if (this.flagged[i]) {
                cell.textContent = '🚩';
            }

            cell.addEventListener('click', () => this.revealCell(i));
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.toggleFlag(i);
            });

            this.gridElement.appendChild(cell);
        }
    }

    revealCell(idx) {
        if (this.gameOver || this.revealed[idx] || this.flagged[idx]) return;

        this.revealed[idx] = true;

        if (this.grid[idx] === 'M') {
            this.gameOver = true;
            this.revealAll();
            alert('Game Over! You hit a mine! 💣');
            return;
        }

        if (this.grid[idx] === 0) {
            // Flood fill
            const row = Math.floor(idx / this.gridSize);
            const col = idx % this.gridSize;

            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    const nr = row + dr;
                    const nc = col + dc;
                    if (nr >= 0 && nr < this.gridSize && nc >= 0 && nc < this.gridSize) {
                        const nidx = nr * this.gridSize + nc;
                        if (!this.revealed[nidx]) {
                            this.revealCell(nidx);
                        }
                    }
                }
            }
        }

        this.updateCounter();
        this.renderGrid();
    }

    toggleFlag(idx) {
        if (!this.revealed[idx]) {
            this.flagged[idx] = !this.flagged[idx];
            this.updateCounter();
            this.renderGrid();
        }
    }

    revealAll() {
        for (let i = 0; i < this.grid.length; i++) {
            this.revealed[i] = true;
        }
        this.renderGrid();
    }

    updateCounter() {
        const remaining = this.mineCount - this.flagged.filter(f => f).length;
        if (this.counterElement) {
            this.counterElement.textContent = Math.max(0, remaining).toString().padStart(3, '0');
        }
    }

    reset() {
        this.initializeGrid();
        this.updateCounter();
        this.renderGrid();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Start Menu
    new StartMenu();

    // Desktop Icons
    document.querySelectorAll('.icon').forEach(icon => {
        new DesktopIcon(icon);
    });

    // Windows
    document.querySelectorAll('.window').forEach(win => {
        new Window(win);
    });

    // Minesweeper
    new Minesweeper();

    // Close start menu when pressing Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const startMenu = document.querySelector('.start-menu-container');
            if (startMenu) {
                startMenu.classList.remove('active');
            }
        }
    });
});
