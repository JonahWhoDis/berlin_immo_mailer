export interface Website {
    url: string;
    lastChecked: Date;
    contentHash: string;
}

export interface ChangeAlert {
    website: Website;
    changes: string[];
    timestamp: Date;
}