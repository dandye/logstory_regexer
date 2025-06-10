// Initialize Socket.IO connection
const socket = io();

// Global state
let currentPatterns = [];
let currentLogType = '';
let patternColors = {};

// DOM elements
const logTypeSelect = document.getElementById('log-type');
const lineLimitInput = document.getElementById('line-limit');
const loadPatternsBtn = document.getElementById('load-patterns');
const analyzeBtn = document.getElementById('analyze');
const addPatternBtn = document.getElementById('add-pattern');
const patternsList = document.getElementById('patterns-list');
const resultsDiv = document.getElementById('results');
const statsDiv = document.getElementById('stats');
const legendItems = document.getElementById('legend-items');
const logFileInput = document.getElementById('log-file');
const uploadFileBtn = document.getElementById('upload-file');
const fileStatusDiv = document.getElementById('file-status');

// Color generation
function generateColorForString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash |= 0;
    }
    const hue = Math.abs(hash % 360);
    return `hsl(${hue}, 70%, 50%)`;
}

function generateGroupColor(baseColor, groupIndex) {
    // Parse HSL color
    const match = baseColor.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (match) {
        const hue = parseInt(match[1]);
        const saturation = parseInt(match[2]);
        const lightness = parseInt(match[3]);
        
        // Modify hue slightly for each group
        const newHue = (hue + groupIndex * 30) % 360;
        const newLightness = Math.min(90, lightness + groupIndex * 10);
        
        return `hsl(${newHue}, ${saturation}%, ${newLightness}%)`;
    }
    return baseColor;
}

// Load patterns from YAML config
async function loadPatterns() {
    currentLogType = logTypeSelect.value;
    
    try {
        const response = await fetch(`/api/patterns/${currentLogType}`);
        const data = await response.json();
        
        if (data.error) {
            alert('Error loading patterns: ' + data.error);
            return;
        }
        
        currentPatterns = data.patterns || [];
        renderPatterns();
        updateLegend();
    } catch (error) {
        alert('Error loading patterns: ' + error.message);
    }
}

// Render pattern list
function renderPatterns() {
    patternsList.innerHTML = '';
    
    currentPatterns.forEach((pattern, index) => {
        const color = generateColorForString(pattern.name || `Pattern ${index + 1}`);
        patternColors[index] = color;
        
        const patternDiv = document.createElement('div');
        patternDiv.className = 'pattern-item';
        patternDiv.innerHTML = `
            <div class="pattern-header">
                <span>
                    <span class="pattern-color" style="background-color: ${color}"></span>
                    <strong>${pattern.name || `Pattern ${index + 1}`}</strong>
                </span>
                <div class="pattern-controls">
                    <button class="btn btn-danger" onclick="removePattern(${index})">Remove</button>
                </div>
            </div>
            <input type="text" class="pattern-name" value="${pattern.name || ''}" 
                   placeholder="Pattern name" onchange="updatePatternName(${index}, this.value)">
            <textarea class="pattern-input" rows="3" 
                      placeholder="Enter regex pattern..."
                      onchange="updatePattern(${index}, this.value)"
                      oninput="validatePattern(${index}, this.value)">${pattern.pattern || ''}</textarea>
        `;
        
        patternsList.appendChild(patternDiv);
    });
}

// Add new pattern
function addPattern() {
    currentPatterns.push({
        name: `Pattern ${currentPatterns.length + 1}`,
        pattern: ''
    });
    renderPatterns();
    updateLegend();
}

// Remove pattern
function removePattern(index) {
    currentPatterns.splice(index, 1);
    renderPatterns();
    updateLegend();
}

// Update pattern name
function updatePatternName(index, name) {
    currentPatterns[index].name = name;
    updateLegend();
}

// Update pattern
function updatePattern(index, pattern) {
    currentPatterns[index].pattern = pattern;
}

// Validate regex pattern
function validatePattern(index, pattern) {
    const input = document.querySelectorAll('.pattern-input')[index];
    
    try {
        new RegExp(pattern);
        input.classList.remove('error');
    } catch (e) {
        input.classList.add('error');
    }
}

// Update legend
function updateLegend() {
    legendItems.innerHTML = '';
    
    currentPatterns.forEach((pattern, index) => {
        if (!pattern.pattern) return;
        
        const color = patternColors[index];
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-color" style="background-color: ${color}"></div>
            <span class="legend-name">${pattern.name || `Pattern ${index + 1}`}</span>
            <span class="legend-pattern">${pattern.pattern}</span>
        `;
        
        legendItems.appendChild(legendItem);
    });
}

// Analyze patterns
function analyze() {
    const lineLimit = parseInt(lineLimitInput.value) || 100;
    
    resultsDiv.innerHTML = '<div class="loading">Analyzing...</div>';
    statsDiv.innerHTML = '';
    
    socket.emit('analyze_patterns', {
        log_type: currentLogType,
        patterns: currentPatterns.filter(p => p.pattern),
        line_limit: lineLimit
    });
}

// Handle analysis results
socket.on('analysis_results', (data) => {
    const { results, total_lines, analyzed_lines } = data;
    
    // Update stats
    const linesWithMatches = results.filter(r => r.matches && r.matches.length > 0).length;
    statsDiv.innerHTML = `
        <strong>Statistics:</strong> 
        Analyzed ${analyzed_lines} of ${total_lines} lines | 
        ${linesWithMatches} lines with matches
    `;
    
    // Clear results
    resultsDiv.innerHTML = '';
    
    // Render results
    results.forEach(lineResult => {
        const lineDiv = document.createElement('div');
        lineDiv.className = 'log-line';
        
        // Process highlights with proper HTML escaping
        const highlightedLine = applyHighlights(lineResult.line, lineResult.matches);
        
        lineDiv.innerHTML = `
            <span class="line-number">${lineResult.line_number}:</span>
            <span>${highlightedLine}</span>
        `;
        
        resultsDiv.appendChild(lineDiv);
    });
});

// Apply highlights to text with proper HTML escaping
function applyHighlights(text, matches) {
    // Collect all highlight regions
    const highlights = [];
    
    matches.forEach(patternMatch => {
        const patternIndex = currentPatterns.findIndex(p => p.name === patternMatch.name);
        const patternColor = patternColors[patternIndex];
        
        patternMatch.matches.forEach(match => {
            // Only visualize capture groups, not the full match
            match.groups.forEach((group, groupIndex) => {
                highlights.push({
                    start: group.start,
                    end: group.end,
                    color: patternColor,
                    type: 'group',
                    groupIndex: group.index,
                    groupNumber: groupIndex + 1,  // For CSS styling
                    patternName: patternMatch.name,
                    priority: 1
                });
            });
        });
    });
    
    // Sort highlights by start position, then by priority (groups before matches)
    highlights.sort((a, b) => {
        if (a.start !== b.start) {
            return a.start - b.start;
        }
        // If same start, prioritize groups over matches
        return b.priority - a.priority;
    });
    
    // Build the highlighted text
    let result = [];
    let lastPos = 0;
    let openSpans = [];
    
    // Create events for opening and closing spans
    const events = [];
    highlights.forEach((highlight, idx) => {
        events.push({
            pos: highlight.start,
            type: 'open',
            highlight: highlight,
            idx: idx
        });
        events.push({
            pos: highlight.end,
            type: 'close',
            highlight: highlight,
            idx: idx
        });
    });
    
    // Sort events by position, then by type (close before open at same position)
    events.sort((a, b) => {
        if (a.pos !== b.pos) {
            return a.pos - b.pos;
        }
        // At same position, close tags come before open tags
        if (a.type !== b.type) {
            return a.type === 'close' ? -1 : 1;
        }
        // For same type at same position, maintain order
        return a.idx - b.idx;
    });
    
    // Process events
    events.forEach(event => {
        // Add text before this event
        if (event.pos > lastPos) {
            const textSegment = text.substring(lastPos, event.pos);
            result.push(escapeHtml(textSegment));
            lastPos = event.pos;
        }
        
        if (event.type === 'open') {
            let className = event.highlight.type === 'group' ? 'highlighted-text group-highlight' : 'highlighted-text';
            const title = event.highlight.type === 'group' ? `Capture Group ${event.highlight.groupIndex}` : 'Full Match';
            const dataPattern = event.highlight.patternName.replace(/\s+/g, '-').toLowerCase();
            
            // Add group number class for styling
            if (event.highlight.type === 'group') {
                className += ` group-${event.highlight.groupNumber}`;
            }
            
            result.push(`<span class="${className}" data-pattern="${dataPattern}" title="${title}">`);
            openSpans.push(event.highlight);
        } else {
            // Close span
            result.push('</span>');
            // Remove from openSpans
            const idx = openSpans.findIndex(s => s === event.highlight);
            if (idx !== -1) {
                openSpans.splice(idx, 1);
            }
        }
    });
    
    // Add any remaining text
    if (lastPos < text.length) {
        result.push(escapeHtml(text.substring(lastPos)));
    }
    
    // Close any unclosed spans (shouldn't happen with correct data)
    while (openSpans.length > 0) {
        result.push('</span>');
        openSpans.pop();
    }
    
    return result.join('');
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Upload file handler
async function uploadFile() {
    const file = logFileInput.files[0];
    if (!file) {
        showFileStatus('Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('log_type', logTypeSelect.value);
    
    showFileStatus('Uploading file...', 'info');
    
    try {
        const response = await fetch('/api/upload-log', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showFileStatus(`File uploaded successfully! ${data.lines} lines loaded.`, 'success');
        } else {
            showFileStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showFileStatus(`Upload failed: ${error.message}`, 'error');
    }
}

// Show file status message
function showFileStatus(message, type) {
    fileStatusDiv.textContent = message;
    fileStatusDiv.className = `file-status ${type}`;
    
    if (type !== 'error') {
        setTimeout(() => {
            fileStatusDiv.className = 'file-status';
        }, 5000);
    }
}

// Event listeners
loadPatternsBtn.addEventListener('click', loadPatterns);
analyzeBtn.addEventListener('click', analyze);
addPatternBtn.addEventListener('click', addPattern);
uploadFileBtn.addEventListener('click', uploadFile);

// Load patterns on page load
window.addEventListener('load', () => {
    if (logTypeSelect.value) {
        loadPatterns();
    }
    
    // Update file status when log type changes
    logTypeSelect.addEventListener('change', () => {
        fileStatusDiv.className = 'file-status';
    });
});