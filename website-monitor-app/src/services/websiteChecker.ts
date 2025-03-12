import axios from 'axios';
import { scanForDifferences } from '../utils/diffScanner';
import { Website, ChangeAlert } from '../types';

export class WebsiteChecker {
    private websites: Website[];
    private previousContents: Map<string, string>;

    constructor(websites: Website[]) {
        this.websites = websites;
        this.previousContents = new Map();
    }

    public async checkWebsites(): Promise<void> {
        for (const website of this.websites) {
            try {
                const response = await axios.get(website.url);
                const currentContent = response.data;

                if (this.previousContents.has(website.url)) {
                    const previousContent = this.previousContents.get(website.url);
                    if (previousContent !== undefined) {
                        const differences = scanForDifferences(previousContent, currentContent);
                        if (differences) {
                            this.alertChanges(website, differences.join('\n'));
                        }
                    }
                }

                this.previousContents.set(website.url, currentContent);
            } catch (error) {
                console.error(`Error checking website ${website.url}:`, error);
            }
        }
    }

    private alertChanges(website: Website, differences: string): void {
        const alert: ChangeAlert = {
            website: website,
            changes: [differences],
            timestamp: new Date(),
        };
        console.log('Change detected:', alert);
        // Here you can implement additional notification logic (e.g., email, SMS)
    }
}