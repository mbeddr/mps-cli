import { JSDOM } from 'jsdom';

export function parseXml(str : string) : XMLDocument {
    const doc = new JSDOM("");
    const DOMParser = doc.window.DOMParser
    const parser = new DOMParser
    return parser.parseFromString(str, "text/xml");
}