import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "Comfy.FileDataBrowser",
    async nodeCreated(node) {
        // Add file browser UI to both node types
        if (node.comfyClass === "EncodedPromptFromFile" || node.comfyClass === "SampledLatentsFromFile") {
            addFileBrowserUI(node);
        }
    }
});

function addFileBrowserUI(node) {
    // Reuse the same configuration from IO_LoadImage
    const DIRECTORY_Y_OFFSET = 30;
    const CLICK_Y_OFFSET = 0;
    const CLICK_X_OFFSET = -2;
    const FAVORITES_Y_OFFSET = 160;
    const DIVIDER_WIDTH = 13;

    const selectedFileWidget = node.widgets.find(w => w.name === "selected_file");
    selectedFileWidget.hidden = true;

    // Constants for sizing
    const MIN_WIDTH = 430;
    const MIN_HEIGHT = 550;
    const TOP_PADDING = 210;
    const BOTTOM_PADDING = 20;
    const FOLDER_HEIGHT = 30;
    const INDENT_WIDTH = 20;
    const TOP_BAR_HEIGHT = 50;
    const THUMBNAIL_SIZE = 100;
    const THUMBNAIL_PADDING = 10;
    const SCROLLBAR_WIDTH = 13;

    // Define colors
    const COLORS = {
        background: "#1e1e1e",
        topBar: "#252526",
        folder: "#2d2d30",
        folderHover: "#3e3e42",
        folderSelected: "#0e639c",
        text: "#cccccc",
        scrollbar: "#3e3e42",
        scrollbarHover: "#505050",
        thumbnailBorder: "#007acc",
        thumbnailBackground: "#252526",
        favoritesTab: "#5e5e5e",
        favoriteButton: "#0e639c",
        favoriteButtonHover: "#1177bb",
        divider: "#4f0074",
        dividerHover: "#16727c"
    };

    // Get the initial output directory from ComfyUI's settings
    let currentDirectory = app.outputPath || "./output";  // Default to ./output if not set
    let selectedFile = selectedFileWidget.value;
    let directoryStructure = { name: "root", children: [], expanded: true, path: currentDirectory };
    let fileList = [];
    let scrollOffsetLeft = 0;
    let scrollOffsetRight = 0;
    let isDraggingLeft = false;
    let isDraggingRight = false;
    let hoveredFolder = null;
    let hoveredFavorite = null;
    let scrollStartY = 0;
    let scrollStartOffset = 0;
    let showFavorites = false;
    let favorites = JSON.parse(localStorage.getItem('fileBrowserFavorites') || '[]');
    let leftColumnWidth = node.size[0] / 2;
    let isDraggingDivider = false;
    let isHoveringDivider = false;

    // Filter function based on node type
    function filterFiles(files) {
        const extensions = node.comfyClass === "EncodedPromptFromFile" 
            ? ['.pkl', '.pt', '.pth', '.safetensors', '.ckpt'] 
            : ['.pkl', '.pt', '.pth', '.bin', '.latent'];
        return files.filter(f => extensions.some(ext => f.toLowerCase().endsWith(ext)));
    }

    async function updateDirectoryStructure() {
        try {
            const response = await fetch('/io_file_browser/get_directory_structure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: currentDirectory })
            });
            const data = await response.json();
            mergeDirectoryStructure(directoryStructure, data.structure);
            fileList = filterFiles(data.files);
            node.setDirtyCanvas(true);
        } catch (error) {
            console.error("Error updating directory structure:", error);
        }
    }

    function mergeDirectoryStructure(existing, updated) {
        existing.name = updated.name;
        existing.path = updated.path;

        const existingChildren = new Map(existing.children.map(child => [child.name, child]));
        existing.children = updated.children.map(updatedChild => {
            const existingChild = existingChildren.get(updatedChild.name);
            if (existingChild) {
                mergeDirectoryStructure(existingChild, updatedChild);
                return existingChild;
            } else {
                return { ...updatedChild, expanded: false };
            }
        });
    }

    function updateSelectedFile(file) {
        selectedFile = file;
        selectedFileWidget.value = currentDirectory + '/' + file;
        node.setDirtyCanvas(true);
    }

    function goUpDirectory() {
        const parentDir = currentDirectory.split(/(\\|\/)/g).slice(0, -2).join('');
        if (parentDir) {
            currentDirectory = parentDir;
            updateDirectoryStructure();
        }
    }

    // Add refresh button
    const refreshButton = node.addWidget("button", "Refresh", null, () => {
        updateDirectoryStructure();
    });

    // Drawing functions
    node.onDrawBackground = function(ctx) {
        if (!this.flags.collapsed) {
            const pos = TOP_PADDING - TOP_BAR_HEIGHT;
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, pos, this.size[0], this.size[1] - pos);

            // Draw top bar with current directory
            ctx.fillStyle = COLORS.topBar;
            ctx.fillRect(0, pos, this.size[0], TOP_BAR_HEIGHT);

            // Draw back button
            drawRoundedRect(ctx, 10, pos + 10, 80, TOP_BAR_HEIGHT - 20, 5, COLORS.folder);
            ctx.fillStyle = COLORS.text;
            ctx.font = "14px Arial";
            ctx.fillText("← Back", 30, pos + 32);

            // Draw current directory
            ctx.fillStyle = COLORS.text;
            ctx.font = "14px Arial";
            ctx.fillText(currentDirectory, 100, pos + 32);

            // Draw file list
            ctx.save();
            ctx.beginPath();
            ctx.rect(0, TOP_PADDING, this.size[0], this.size[1] - TOP_PADDING - BOTTOM_PADDING);
            ctx.clip();

            let y = TOP_PADDING;
            fileList.forEach((file, index) => {
                const isSelected = file === selectedFile;
                const isHovered = index === hoveredFile;

                if (isSelected || isHovered) {
                    drawRoundedRect(ctx, 10, y, this.size[0] - 20, FOLDER_HEIGHT, 5, 
                        isSelected ? COLORS.folderSelected : COLORS.folderHover);
                }

                ctx.fillStyle = COLORS.text;
                ctx.font = "14px Arial";
                ctx.fillText(file, 20, y + FOLDER_HEIGHT/2 + 5);

                y += FOLDER_HEIGHT;
            });

            ctx.restore();
        }
    };

    // Mouse handling
    node.onMouseDown = function(event) {
        const pos = TOP_PADDING - TOP_BAR_HEIGHT;
        const localY = event.canvasY - this.pos[1] - pos + CLICK_Y_OFFSET;
        const localX = event.canvasX - this.pos[0] + CLICK_X_OFFSET;

        if (localY >= 0 && localY <= TOP_BAR_HEIGHT) {
            // Handle back button click
            if (localX >= 10 && localX <= 90 && localY >= 10 && localY <= TOP_BAR_HEIGHT - 10) {
                goUpDirectory();
                return true;
            }
        } else {
            // Handle file selection
            const fileIndex = Math.floor((localY - TOP_PADDING) / FOLDER_HEIGHT);
            if (fileIndex >= 0 && fileIndex < fileList.length) {
                updateSelectedFile(fileList[fileIndex]);
                return true;
            }
        }

        return false;
    };

    // Initialize
    updateDirectoryStructure();

    // Set minimum size
    node.size[0] = Math.max(MIN_WIDTH, node.size[0]);
    node.size[1] = Math.max(MIN_HEIGHT, node.size[1]);
}

// Helper function to draw rounded rectangles
function drawRoundedRect(ctx, x, y, width, height, radius, color) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
}