// Windows 98 Desktop Shell - JavaScript

// Global state
let highestZIndex = 100;
const windowRegistry = new Map();

// Utility function to detect if device supports touch
const isTouchDevice = () => 'ontouchstart' in window || navigator.maxTouchPoints > 0;

class LoadingOverlay {
    constructor() {
        this.overlay = document.getElementById('loading-overlay');
        if (!this.overlay) return;

        this.video = document.getElementById('loading-video');
        this.progressBar = this.overlay.querySelector('.loading-progress__bar');
        this.progressValue = 0;
        this.progressInterval = null;
        this.failSafeTimeout = null;
        this.failSafeDelay = null;
        this.isComplete = false;

        this.init();
    }

    init() {
        this.overlay.setAttribute('aria-hidden', 'false');
        document.body.classList.add('loading-active');
        this.startProgress();

        if (this.video) {
            this.video.muted = true;
            this.video.setAttribute('muted', '');
            this.video.setAttribute('playsinline', '');
            this.video.setAttribute('autoplay', '');
            this.video.addEventListener('loadeddata', () => this.handleLoadedData());
            this.video.addEventListener('ended', () => this.complete());
            this.video.addEventListener('error', () => this.handleError());

            const playPromise = this.video.play();
            if (playPromise && typeof playPromise.then === 'function') {
                playPromise.catch(() => {
                    this.scheduleFallback(3500);
                });
            }
        } else {
            this.scheduleFallback(1200);
        }

        window.addEventListener('load', () => this.complete());
        this.scheduleFallback(6000);
    }

    startProgress() {
        this.setProgress(4);

        this.progressInterval = setInterval(() => {
            if (this.isComplete) return;
            const increment = 5 + Math.random() * 6;
            const nextValue = Math.min(95, this.progressValue + increment);
            this.setProgress(nextValue);
        }, 260);
    }

    handleLoadedData() {
        this.setProgress(Math.max(this.progressValue, 45));
        this.scheduleFallback(1800);
    }

    handleError() {
        this.scheduleFallback(800);
    }

    scheduleFallback(delay) {
        if (this.isComplete) return;

        if (!this.failSafeTimeout || delay < this.failSafeDelay) {
            if (this.failSafeTimeout) {
                clearTimeout(this.failSafeTimeout);
            }

            this.failSafeDelay = delay;
            this.failSafeTimeout = setTimeout(() => this.complete(), delay);
        }
    }

    setProgress(value) {
        this.progressValue = Math.max(0, Math.min(100, value));

        if (this.progressBar) {
            this.progressBar.style.width = `${this.progressValue}%`;
            this.progressBar.setAttribute('aria-valuenow', Math.round(this.progressValue).toString());
        }
    }

    complete() {
        if (this.isComplete) return;
        this.isComplete = true;

        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }

        if (this.failSafeTimeout) {
            clearTimeout(this.failSafeTimeout);
            this.failSafeTimeout = null;
        }

        this.setProgress(100);
        document.body.classList.remove('loading-active');

        if (!this.overlay) return;

        this.overlay.setAttribute('aria-hidden', 'true');

        const handleTransitionEnd = () => {
            this.overlay.removeEventListener('transitionend', handleTransitionEnd);
            this.overlay.style.display = 'none';
        };

        this.overlay.addEventListener('transitionend', handleTransitionEnd);
        requestAnimationFrame(() => {
            this.overlay.classList.add('hidden');
        });

        setTimeout(() => {
            this.overlay.style.display = 'none';
        }, 500);
    }
}

// Start Menu
class StartMenu {
    constructor() {
        this.startButton = document.querySelector('.start-button');
        this.menuContainer = document.querySelector('.start-menu-container');
        this.menuItems = document.querySelectorAll('.start-menu-item');
        this.isOpen = false;
        this.init();
    }

    init() {
        // Use pointer events for unified mouse/touch handling
        this.startButton.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            this.toggle();
        });
        
        document.addEventListener('pointerdown', (e) => this.handleOutsideClick(e));
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Wire up menu items
        this.menuItems.forEach(item => {
            item.addEventListener('pointerdown', (e) => {
                e.preventDefault();
                this.handleMenuItemClick(item);
            });
        });
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.menuContainer.classList.add('active');
        this.isOpen = true;
    }

    close() {
        this.menuContainer.classList.remove('active');
        this.isOpen = false;
    }

    handleOutsideClick(e) {
        if (this.isOpen && 
            !e.target.closest('.start-button') && 
            !e.target.closest('.start-menu-container')) {
            this.close();
        }
    }

    handleMenuItemClick(item) {
        const text = item.textContent.trim();
        const windowId = item.dataset.windowId;
        const action = item.dataset.action;
        
        console.log(`Menu item clicked: ${text}`);
        
        if (windowId) {
            this.openWindowById(windowId);
        } else if (action === 'shutdown') {
            alert('Shutting down... (demo)');
        }
        
        this.close();
    }

    openWindowById(windowId) {
        const windowElement = document.getElementById(windowId);
        
        if (windowElement && windowRegistry.has(windowElement)) {
            const windowInstance = windowRegistry.get(windowElement);
            windowInstance.restore();
            windowInstance.focus();
        } else if (windowElement) {
            console.warn(`Window element found but not in registry: ${windowId}`);
        } else {
            console.warn(`Window not found: ${windowId}`);
        }
    }
}

// Desktop Icons
class DesktopIcon {
    constructor(element) {
        this.element = element;
        this.isSelected = false;
        this.lastTapTime = 0;
        this.longPressTimer = null;
        this.element._desktopIconInstance = this;
        this.init();
    }

    init() {
        // Unified pointer events
        this.element.addEventListener('pointerdown', (e) => this.handlePointerDown(e));
        
        // For desktop: double-click
        this.element.addEventListener('dblclick', () => this.open());

        // Hover effect for mouse
        this.element.addEventListener('pointerenter', (e) => {
            if (e.pointerType === 'mouse') {
                this.element.style.filter = 'brightness(1.1)';
            }
        });
        
        this.element.addEventListener('pointerleave', (e) => {
            if (e.pointerType === 'mouse') {
                this.element.style.filter = '';
            }
        });
    }

    handlePointerDown(e) {
        const currentTime = Date.now();
        const timeSinceLastTap = currentTime - this.lastTapTime;

        // Single click/tap: select
        this.select();

        // Double-tap detection for touch devices (within 500ms)
        if (e.pointerType === 'touch' && timeSinceLastTap < 500) {
            this.open();
            this.lastTapTime = 0;
            if (this.longPressTimer) {
                clearTimeout(this.longPressTimer);
                this.longPressTimer = null;
            }
        } else {
            this.lastTapTime = currentTime;
            
            // Long-press for touch devices (600ms)
            if (e.pointerType === 'touch') {
                if (this.longPressTimer) {
                    clearTimeout(this.longPressTimer);
                }
                this.longPressTimer = setTimeout(() => {
                    this.showContextMenu();
                    this.longPressTimer = null;
                }, 600);
            }
        }

        // Cancel long-press on pointer up/cancel
        const cancelLongPress = () => {
            if (this.longPressTimer) {
                clearTimeout(this.longPressTimer);
                this.longPressTimer = null;
            }
            this.element.removeEventListener('pointerup', cancelLongPress);
            this.element.removeEventListener('pointercancel', cancelLongPress);
        };
        
        this.element.addEventListener('pointerup', cancelLongPress);
        this.element.addEventListener('pointercancel', cancelLongPress);
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
        const windowId = this.element.dataset.windowId;
        console.log(`Opening: ${label} (Window ID: ${windowId})`);
        
        if (windowId) {
            const windowElement = document.getElementById(windowId);
            
            if (windowElement && windowRegistry.has(windowElement)) {
                const windowInstance = windowRegistry.get(windowElement);
                windowInstance.restore();
                windowInstance.focus();
            } else if (windowElement) {
                console.warn(`Window element found but not in registry: ${windowId}`);
            } else {
                console.warn(`Window not found: ${windowId}`);
            }
        }
    }

    showContextMenu() {
        // Visual feedback for long-press
        this.element.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.element.style.transform = '';
        }, 200);
        console.log('Long-press detected on:', this.element.querySelector('.icon-label').textContent);
    }
}

// Window Management
class Window {
    constructor(element) {
        this.element = element;
        this.isDragging = false;
        this.dragOffsetX = 0;
        this.dragOffsetY = 0;
        this.state = 'normal'; // normal, minimized, maximized
        this.normalPosition = { left: 0, top: 0, width: 0, height: 0 };
        this.taskbarButton = null;
        this.pointerId = null;
        
        // Store original styles for restore
        this.originalStyles = {
            position: this.element.style.position || 'relative',
            left: this.element.style.left || 'auto',
            top: this.element.style.top || 'auto',
            width: this.element.style.width || 'auto',
            height: this.element.style.height || 'auto',
            margin: this.element.style.margin || '20px auto',
            maxWidth: this.element.style.maxWidth || '800px'
        };
        
        this.init();
        windowRegistry.set(element, this);
    }

    init() {
        const titleBar = this.element.querySelector('.title-bar');
        if (titleBar) {
            titleBar.addEventListener('pointerdown', (e) => this.startDrag(e));
        }

        // Close button
        const closeBtn = this.element.querySelector('.title-bar-button:nth-child(3)');
        if (closeBtn) {
            closeBtn.addEventListener('pointerdown', (e) => {
                e.stopPropagation();
                this.close();
            });
        }

        // Minimize button
        const minimizeBtn = this.element.querySelector('.title-bar-button:nth-child(1)');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('pointerdown', (e) => {
                e.stopPropagation();
                this.minimize();
            });
        }

        // Maximize button
        const maximizeBtn = this.element.querySelector('.title-bar-button:nth-child(2)');
        if (maximizeBtn) {
            maximizeBtn.addEventListener('pointerdown', (e) => {
                e.stopPropagation();
                this.toggleMaximize();
            });
        }

        // Focus on click
        this.element.addEventListener('pointerdown', (e) => {
            if (!e.target.closest('.title-bar-button')) {
                this.focus();
            }
        });

        // Set initial position if not set
        if (this.element.style.position !== 'fixed') {
            const rect = this.element.getBoundingClientRect();
            this.element.style.position = 'fixed';
            this.element.style.left = rect.left + 'px';
            this.element.style.top = rect.top + 'px';
            this.element.style.margin = '0';
            this.element.style.width = rect.width + 'px';
        }

        this.saveNormalPosition();
    }

    startDrag(e) {
        if (e.target.closest('.title-bar-button')) return;
        if (this.state === 'maximized') return;
        
        e.preventDefault();
        this.isDragging = true;
        this.pointerId = e.pointerId;
        
        const rect = this.element.getBoundingClientRect();
        this.dragOffsetX = e.clientX - rect.left;
        this.dragOffsetY = e.clientY - rect.top;

        // Set pointer capture for better touch handling
        e.target.setPointerCapture(e.pointerId);

        // Remove transition during drag for smooth movement
        this.element.style.transition = 'none';

        const moveHandler = (e) => this.drag(e);
        const upHandler = (e) => this.stopDrag(e, moveHandler, upHandler);

        document.addEventListener('pointermove', moveHandler);
        document.addEventListener('pointerup', upHandler);
        document.addEventListener('pointercancel', upHandler);

        this.focus();
    }

    drag(e) {
        if (!this.isDragging || e.pointerId !== this.pointerId) return;
        
        e.preventDefault();
        
        const x = e.clientX - this.dragOffsetX;
        const y = e.clientY - this.dragOffsetY;

        // Keep window within viewport bounds
        const maxX = window.innerWidth - 100; // Leave some space
        const maxY = window.innerHeight - 100;
        
        this.element.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
        this.element.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
    }

    stopDrag(e, moveHandler, upHandler) {
        if (e.pointerId !== this.pointerId) return;
        
        this.isDragging = false;
        this.pointerId = null;
        
        // Re-enable transitions
        this.element.style.transition = '';
        
        document.removeEventListener('pointermove', moveHandler);
        document.removeEventListener('pointerup', upHandler);
        document.removeEventListener('pointercancel', upHandler);
        
        this.saveNormalPosition();
    }

    focus() {
        highestZIndex++;
        this.element.style.zIndex = highestZIndex;
        
        // Update title bar to show focused state
        document.querySelectorAll('.window').forEach(win => {
            const titleBar = win.querySelector('.title-bar');
            if (titleBar) {
                titleBar.classList.remove('focused');
            }
        });
        
        const titleBar = this.element.querySelector('.title-bar');
        if (titleBar) {
            titleBar.classList.add('focused');
        }
    }

    close() {
        this.element.style.opacity = '0';
        this.element.style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            this.element.style.display = 'none';
            this.element.style.opacity = '';
            this.element.style.transform = '';
            this.removeTaskbarButton();
        }, 200);
    }

    minimize() {
        if (this.state === 'minimized') return;
        
        this.saveNormalPosition();
        this.state = 'minimized';
        
        // Animate to taskbar
        const taskbar = document.querySelector('.taskbar');
        const taskbarRect = taskbar.getBoundingClientRect();
        
        this.element.style.opacity = '0';
        this.element.style.transform = 'scale(0.1)';
        
        setTimeout(() => {
            this.element.style.display = 'none';
            this.element.style.opacity = '';
            this.element.style.transform = '';
            this.addTaskbarButton();
        }, 200);
    }

    toggleMaximize() {
        if (this.state === 'maximized') {
            this.restore();
        } else {
            this.maximize();
        }
    }

    maximize() {
        if (this.state === 'maximized') return;
        
        this.saveNormalPosition();
        this.state = 'maximized';
        
        // Calculate viewport dimensions respecting taskbar
        const taskbar = document.querySelector('.taskbar');
        const taskbarHeight = taskbar ? taskbar.offsetHeight : 40;
        
        // Get viewport width for responsive behavior
        const viewportWidth = window.innerWidth;
        let targetWidth, targetLeft;
        
        // Respect responsive breakpoints
        if (viewportWidth <= 480) {
            targetWidth = viewportWidth - 10;
            targetLeft = 5;
        } else if (viewportWidth <= 768) {
            targetWidth = viewportWidth - 20;
            targetLeft = 10;
        } else if (viewportWidth <= 1024) {
            targetWidth = viewportWidth - 40;
            targetLeft = 20;
        } else {
            targetWidth = viewportWidth - 80;
            targetLeft = 40;
        }
        
        this.element.style.left = targetLeft + 'px';
        this.element.style.top = '0px';
        this.element.style.width = targetWidth + 'px';
        this.element.style.height = (window.innerHeight - taskbarHeight) + 'px';
        this.element.style.maxWidth = 'none';
        
        this.focus();
    }

    restore() {
        if (this.state === 'normal') return;
        
        const wasMinimized = this.state === 'minimized';
        this.state = 'normal';
        
        if (wasMinimized) {
            this.element.style.display = 'flex';
            this.element.style.opacity = '0';
            this.element.style.transform = 'scale(0.9)';
            
            requestAnimationFrame(() => {
                this.element.style.opacity = '1';
                this.element.style.transform = 'scale(1)';
            });
            
            this.removeTaskbarButton();
        } else {
            // Restore from maximized
            this.element.style.left = this.normalPosition.left + 'px';
            this.element.style.top = this.normalPosition.top + 'px';
            this.element.style.width = this.normalPosition.width + 'px';
            this.element.style.height = this.normalPosition.height + 'px';
            this.element.style.maxWidth = this.originalStyles.maxWidth;
        }
        
        this.focus();
    }

    saveNormalPosition() {
        if (this.state === 'normal') {
            const rect = this.element.getBoundingClientRect();
            this.normalPosition = {
                left: rect.left,
                top: rect.top,
                width: rect.width,
                height: rect.height
            };
        }
    }

    addTaskbarButton() {
        if (this.taskbarButton) return;
        
        const taskbar = document.querySelector('.taskbar');
        const titleText = this.element.querySelector('.title-bar-text').textContent;
        
        const button = document.createElement('button');
        button.className = 'taskbar-window-button';
        button.textContent = titleText;
        button.dataset.windowId = Array.from(windowRegistry.keys()).indexOf(this.element);
        
        button.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            this.restore();
        });
        
        // Insert before clock (if exists) or at the end
        const clock = taskbar.querySelector('.taskbar-clock');
        if (clock) {
            taskbar.insertBefore(button, clock);
        } else {
            taskbar.appendChild(button);
        }
        
        this.taskbarButton = button;
    }

    removeTaskbarButton() {
        if (this.taskbarButton) {
            this.taskbarButton.remove();
            this.taskbarButton = null;
        }
    }
}

// Taskbar Clock
class TaskbarClock {
    constructor() {
        this.clockElement = null;
        this.init();
    }

    init() {
        // Create clock element
        const taskbar = document.querySelector('.taskbar');
        if (!taskbar) return;
        
        this.clockElement = document.createElement('div');
        this.clockElement.className = 'taskbar-clock';
        taskbar.appendChild(this.clockElement);
        
        // Update immediately and then every minute
        this.updateTime();
        setInterval(() => this.updateTime(), 60000); // Update every minute
        
        // Also update every second for the first minute to ensure accuracy
        const secondInterval = setInterval(() => this.updateTime(), 1000);
        setTimeout(() => clearInterval(secondInterval), 60000);
    }

    updateTime() {
        if (!this.clockElement) return;
        
        const now = new Date();
        
        // Format time with locale support
        const timeString = now.toLocaleTimeString(navigator.language || 'en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
        
        this.clockElement.textContent = timeString;
    }
}

// Minesweeper Game
class Minesweeper {
    constructor() {
        this.gridElement = document.getElementById('minesweeper-grid');
        this.mineCounterElement = document.getElementById('mine-counter');
        this.timerElement = document.getElementById('timer');
        this.smileyElement = document.getElementById('smiley-button');
        this.difficultyElement = document.querySelector('.minesweeper-difficulty');
        this.windowElement = document.getElementById('minesweeper-window');
        
        // Difficulty configurations
        this.difficulties = {
            beginner: { rows: 9, cols: 9, mines: 10 },
            intermediate: { rows: 16, cols: 16, mines: 40 },
            expert: { rows: 16, cols: 30, mines: 99 }
        };
        
        // Game state
        this.currentDifficulty = 'beginner';
        this.rows = 9;
        this.cols = 9;
        this.mineCount = 10;
        this.grid = [];
        this.revealed = [];
        this.flagged = [];
        this.gameState = 'ready'; // ready, playing, won, lost
        this.firstClick = true;
        this.timer = 0;
        this.timerInterval = null;
        this.currentCell = null; // For keyboard navigation
        
        this.init();
    }

    init() {
        if (!this.gridElement) return;
        
        this.setupEventListeners();
        this.newGame();
    }

    setupEventListeners() {
        // Smiley reset button
        if (this.smileyElement) {
            this.smileyElement.addEventListener('pointerdown', (e) => {
                e.preventDefault();
                this.setSmileyState('pressed');
            });
            
            this.smileyElement.addEventListener('pointerup', (e) => {
                e.preventDefault();
                this.setSmileyState('normal');
                this.newGame();
            });
            
            this.smileyElement.addEventListener('pointerleave', () => {
                if (this.gameState !== 'won' && this.gameState !== 'lost') {
                    this.setSmileyState('normal');
                }
            });
        }

        // Difficulty selector
        if (this.difficultyElement) {
            this.difficultyElement.addEventListener('change', (e) => {
                this.currentDifficulty = e.target.value;
                this.newGame();
                this.updateWindowStyling();
            });
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (document.activeElement === this.difficultyElement) return;
            
            // Only handle keys when minesweeper window is focused
            const windowInstance = windowRegistry.get(this.windowElement);
            if (!windowInstance || this.windowElement.style.zIndex !== highestZIndex.toString()) return;
            
            switch(e.key) {
                case 'ArrowUp':
                case 'ArrowDown':
                case 'ArrowLeft':
                case 'ArrowRight':
                    e.preventDefault();
                    this.handleArrowKey(e.key);
                    break;
                case ' ':
                case 'Enter':
                    e.preventDefault();
                    if (this.currentCell !== null) {
                        this.revealCell(this.currentCell);
                    }
                    break;
                case 'f':
                case 'F':
                    e.preventDefault();
                    if (this.currentCell !== null) {
                        this.toggleFlag(this.currentCell);
                    }
                    break;
                case 'r':
                case 'R':
                    e.preventDefault();
                    this.newGame();
                    break;
            }
        });
    }

    handleArrowKey(key) {
        if (this.currentCell === null) {
            this.currentCell = 0;
        } else {
            const row = Math.floor(this.currentCell / this.cols);
            const col = this.currentCell % this.cols;
            let newRow = row, newCol = col;

            switch(key) {
                case 'ArrowUp': newRow = Math.max(0, row - 1); break;
                case 'ArrowDown': newRow = Math.min(this.rows - 1, row + 1); break;
                case 'ArrowLeft': newCol = Math.max(0, col - 1); break;
                case 'ArrowRight': newCol = Math.min(this.cols - 1, col + 1); break;
            }

            this.currentCell = newRow * this.cols + newCol;
        }
        this.highlightCurrentCell();
    }

    highlightCurrentCell() {
        // Remove previous highlights
        document.querySelectorAll('.mine-cell.keyboard-focus').forEach(cell => {
            cell.classList.remove('keyboard-focus');
        });

        // Add highlight to current cell
        if (this.currentCell !== null) {
            const cell = this.gridElement.children[this.currentCell];
            if (cell) {
                cell.classList.add('keyboard-focus');
                cell.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
            }
        }
    }

    newGame() {
        // Stop timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }

        // Set difficulty
        const config = this.difficulties[this.currentDifficulty];
        this.rows = config.rows;
        this.cols = config.cols;
        this.mineCount = config.mines;

        // Reset game state
        this.grid = Array(this.rows * this.cols).fill(0);
        this.revealed = Array(this.rows * this.cols).fill(false);
        this.flagged = Array(this.rows * this.cols).fill(false);
        this.gameState = 'ready';
        this.firstClick = true;
        this.timer = 0;
        this.currentCell = null;

        // Update UI
        this.updateMineCounter();
        this.updateTimer();
        this.setSmileyState('normal');
        this.renderGrid();
    }

    initializeMines(excludeIdx) {
        // Place mines randomly, excluding the first clicked cell and its neighbors
        const excludeSet = new Set([excludeIdx]);
        const row = Math.floor(excludeIdx / this.cols);
        const col = excludeIdx % this.cols;

        // Add neighbors to exclude set
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                const nr = row + dr;
                const nc = col + dc;
                if (nr >= 0 && nr < this.rows && nc >= 0 && nc < this.cols) {
                    excludeSet.add(nr * this.cols + nc);
                }
            }
        }

        let minesPlaced = 0;
        while (minesPlaced < this.mineCount) {
            const idx = Math.floor(Math.random() * this.grid.length);
            if (!excludeSet.has(idx) && this.grid[idx] !== 'M') {
                this.grid[idx] = 'M';
                minesPlaced++;
            }
        }

        // Calculate numbers
        for (let i = 0; i < this.grid.length; i++) {
            if (this.grid[i] === 'M') continue;
            
            let count = 0;
            const row = Math.floor(i / this.cols);
            const col = i % this.cols;

            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    if (dr === 0 && dc === 0) continue;
                    const nr = row + dr;
                    const nc = col + dc;
                    if (nr >= 0 && nr < this.rows && nc >= 0 && nc < this.cols) {
                        const idx = nr * this.cols + nc;
                        if (this.grid[idx] === 'M') count++;
                    }
                }
            }
            
            if (count > 0) this.grid[i] = count;
        }
    }

    renderGrid() {
        this.gridElement.innerHTML = '';
        this.gridElement.className = `minesweeper-grid ${this.currentDifficulty}`;
        
        for (let i = 0; i < this.grid.length; i++) {
            const cell = document.createElement('div');
            cell.className = 'mine-cell';
            
            if (this.revealed[i]) {
                cell.classList.add('revealed');
                if (this.grid[i] === 'M') {
                    cell.textContent = '💣';
                } else if (this.grid[i] > 0) {
                    cell.textContent = this.grid[i];
                    cell.setAttribute('data-number', this.grid[i]);
                }
            } else if (this.flagged[i]) {
                cell.textContent = '🚩';
            }

            // Mouse/touch events
            cell.addEventListener('pointerdown', (e) => {
                e.preventDefault();
                this.handleCellPointerDown(i, e);
            });
            
            cell.addEventListener('pointerup', (e) => {
                e.preventDefault();
                this.handleCellPointerUp(i, e);
            });

            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.toggleFlag(i);
            });

            // Hover effect for keyboard focus
            cell.addEventListener('pointerenter', () => {
                if (e.pointerType === 'mouse') {
                    this.currentCell = i;
                    this.highlightCurrentCell();
                }
            });

            this.gridElement.appendChild(cell);
        }
    }

    handleCellPointerDown(idx, e) {
        if (this.gameState === 'won' || this.gameState === 'lost') return;
        if (this.revealed[idx] || this.flagged[idx]) return;

        this.currentCell = idx;
        this.highlightCurrentCell();

        if (e.pointerType === 'touch') {
            // Long-press to flag on touch devices
            this.longPressTimer = setTimeout(() => {
                this.toggleFlag(idx);
                this.longPressTimer = null;
            }, 500);
        }

        // Show pressed smiley
        if (this.gameState === 'playing') {
            this.setSmileyState('surprised');
        }
    }

    handleCellPointerUp(idx, e) {
        if (this.longPressTimer) {
            clearTimeout(this.longPressTimer);
            this.longPressTimer = null;
            
            // This was a click, not a long press
            if (e.pointerType === 'touch' || e.button === 0) {
                this.revealCell(idx);
            }
        }

        // Restore normal smiley
        if (this.gameState === 'playing') {
            this.setSmileyState('normal');
        }
    }

    revealCell(idx) {
        if (this.gameState === 'won' || this.gameState === 'lost') return;
        if (this.revealed[idx] || this.flagged[idx]) return;

        // First click - place mines
        if (this.firstClick) {
            this.firstClick = false;
            this.initializeMines(idx);
            this.gameState = 'playing';
            this.startTimer();
        }

        this.revealed[idx] = true;

        if (this.grid[idx] === 'M') {
            this.gameOver(false);
            return;
        }

        // Flood fill for empty cells
        if (this.grid[idx] === 0) {
            this.floodFill(idx);
        }

        this.checkWinCondition();
        this.renderGrid();
        this.updateMineCounter();
    }

    floodFill(startIdx) {
        const queue = [startIdx];
        const visited = new Set();

        while (queue.length > 0) {
            const idx = queue.shift();
            if (visited.has(idx)) continue;
            visited.add(idx);

            const row = Math.floor(idx / this.cols);
            const col = idx % this.cols;

            for (let dr = -1; dr <= 1; dr++) {
                for (let dc = -1; dc <= 1; dc++) {
                    const nr = row + dr;
                    const nc = col + dc;
                    if (nr >= 0 && nr < this.rows && nc >= 0 && nc < this.cols) {
                        const nidx = nr * this.cols + nc;
                        if (!this.revealed[nidx] && !this.flagged[nidx]) {
                            this.revealed[nidx] = true;
                            if (this.grid[nidx] === 0) {
                                queue.push(nidx);
                            }
                        }
                    }
                }
            }
        }
    }

    toggleFlag(idx) {
        if (this.gameState === 'won' || this.gameState === 'lost') return;
        if (this.revealed[idx]) return;

        this.flagged[idx] = !this.flagged[idx];
        this.updateMineCounter();
        this.renderGrid();
        this.checkWinCondition();
    }

    checkWinCondition() {
        let cellsToReveal = 0;
        let correctFlags = 0;

        for (let i = 0; i < this.grid.length; i++) {
            if (this.grid[i] !== 'M' && !this.revealed[i]) {
                cellsToReveal++;
            }
            if (this.grid[i] === 'M' && this.flagged[i]) {
                correctFlags++;
            }
        }

        if (cellsToReveal === 0 || correctFlags === this.mineCount) {
            this.gameOver(true);
        }
    }

    gameOver(won) {
        this.gameState = won ? 'won' : 'lost';
        this.stopTimer();

        // Reveal all mines
        for (let i = 0; i < this.grid.length; i++) {
            if (this.grid[i] === 'M') {
                this.revealed[i] = true;
            }
        }

        this.setSmileyState(won ? 'cool' : 'dead');
        this.renderGrid();

        // Show game over message
        setTimeout(() => {
            const message = won ? 
                `Congratulations! You won in ${this.timer} seconds! 😎` : 
                'Game Over! You hit a mine! 💣';
            alert(message);
        }, 100);
    }

    startTimer() {
        this.timerInterval = setInterval(() => {
            this.timer++;
            this.updateTimer();
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    updateMineCounter() {
        const remaining = this.mineCount - this.flagged.filter(f => f).length;
        if (this.mineCounterElement) {
            this.mineCounterElement.textContent = Math.max(0, remaining).toString().padStart(3, '0');
        }
    }

    updateTimer() {
        if (this.timerElement) {
            this.timerElement.textContent = Math.min(999, this.timer).toString().padStart(3, '0');
        }
    }

    setSmileyState(state) {
        if (!this.smileyElement) return;
        
        const smileys = {
            normal: '😊',
            pressed: '😮',
            surprised: '😲',
            cool: '😎',
            dead: '😵'
        };
        
        this.smileyElement.textContent = smileys[state] || smileys.normal;
    }

    updateWindowStyling() {
        if (!this.windowElement) return;
        
        // Remove all difficulty classes
        this.windowElement.classList.remove('intermediate', 'expert');
        
        // Add current difficulty class
        if (this.currentDifficulty !== 'beginner') {
            this.windowElement.classList.add(this.currentDifficulty);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Loading Overlay
    new LoadingOverlay();

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
    
    // Taskbar Clock
    new TaskbarClock();

    // Deselect icons when clicking on desktop
    document.getElementById('desktop').addEventListener('pointerdown', (e) => {
        if (e.target === e.currentTarget) {
            document.querySelectorAll('.icon').forEach(icon => {
                icon.classList.remove('selected');
            });
        }
    });
});
