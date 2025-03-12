export function scanForDifferences(previousContent: string, currentContent: string): string[] {
    const previousLines = previousContent.split('\n');
    const currentLines = currentContent.split('\n');
    const differences: string[] = [];

    previousLines.forEach((line, index) => {
        if (line !== currentLines[index]) {
            differences.push(`Line ${index + 1} changed: "${line}" to "${currentLines[index]}"`);
        }
    });

    if (currentLines.length > previousLines.length) {
        for (let i = previousLines.length; i < currentLines.length; i++) {
            differences.push(`Line ${i + 1} added: "${currentLines[i]}"`);
        }
    }

    return differences;
}