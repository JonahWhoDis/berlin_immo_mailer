import fs from 'fs';
import path from 'path';

interface Website {
    comapnyName: string; // note: typo in key, change as needed
    website: string;
}

// Path to the JSON file
const websitesFilePath = path.join(__dirname, 'websites.json');

// Read and parse the JSON file
let websites: Website[] = [];
try {
    const data = fs.readFileSync(websitesFilePath, { encoding: 'utf-8' });
    websites = JSON.parse(data);
    console.log(`Loaded ${websites.length} websites.`);
} catch (error) {
    console.error('Error reading websites.json:', error);
    process.exit(1);
}

// Example function to check a website for changes
async function checkWebsite(url: string): Promise<void> {
    // ...existing code for checking website changes...
    console.log(`Checking ${url}`);
}

// Iterate over the websites and check each one
(async () => {
    for (const site of websites) {
        await checkWebsite(site.website);
    }
})();