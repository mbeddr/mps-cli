import { JSDOM } from 'jsdom';

export function parseXml(str : string) : XMLDocument {
    const doc = new JSDOM(str);
    return doc.window.document
}