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
        console.log(`Menu item clicked: ${text}`);
        
        // Map menu items to actions
        const actionMap = {
            '📁 File': () => this.openWindowByLabel('Portfolio'),
            '✏️ Edit': () => console.log('Edit clicked'),
            '👁️ View': () => console.log('View clicked'),
            '⚙️ Settings': () => console.log('Settings clicked'),
            '🔍 Search': () => console.log('Search clicked'),
            '💬 Help': () => this.openWindowByLabel('About'),
            '🚪 Shut Down': () => alert('Shutting down... (demo)')
        };

        const action = actionMap[text];
        if (action) {
            action();
        }
        
        this.close();
    }

    openWindowByLabel(label) {
        const icon = Array.from(document.querySelectorAll('.icon'))
            .find(el => el.querySelector('.icon-label').textContent === label);
        if (icon) {
            const desktopIcon = icon._desktopIconInstance;
            if (desktopIcon) {
                desktopIcon.open();
            }
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
        console.log(`Opening: ${label}`);
        
        // Map icon labels to windows
        const windowMap = {
            'About': 'About.txt',
            'Portfolio': 'Welcome.txt',
            'Team': 'About.txt',
            'Projects': 'Welcome.txt',
            'Reviews': 'About.txt',
            'Order': 'Welcome.txt'
        };

        const windowTitle = windowMap[label];
        if (windowTitle) {
            const windowElement = Array.from(document.querySelectorAll('.window'))
                .find(win => win.querySelector('.title-bar-text').textContent === windowTitle);
            
            if (windowElement && windowRegistry.has(windowElement)) {
                const windowInstance = windowRegistry.get(windowElement);
                windowInstance.restore();
                windowInstance.focus();
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
            this.smileyElement.addEventListener('pointerdown', (e) => {
                e.preventDefault();
                this.reset();
            });
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

            cell.addEventListener('pointerdown', (e) => {
                e.preventDefault();
                this.revealCell(i);
            });
            
            cell.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.toggleFlag(i);
            });
            
            // Long-press to flag on touch devices
            let longPressTimer = null;
            cell.addEventListener('pointerdown', (e) => {
                if (e.pointerType === 'touch') {
                    longPressTimer = setTimeout(() => {
                        this.toggleFlag(i);
                        longPressTimer = null;
                    }, 500);
                }
            });
            
            cell.addEventListener('pointerup', () => {
                if (longPressTimer) {
                    clearTimeout(longPressTimer);
                    longPressTimer = null;
                }
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
            setTimeout(() => alert('Game Over! You hit a mine! 💣'), 100);
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
