// Log levels system - shared between frontend and backend
export const logger = {
    debug: (...args: any[]) => console.debug(...args),    // Logs detalhados/verbose (DevTools only)
    info: (...args: any[]) => console.info(...args),      // Informações importantes
    log: (...args: any[]) => console.log(...args),        // Logs normais
    warn: (...args: any[]) => console.warn(...args),      // Avisos
    error: (...args: any[]) => console.error(...args)     // Erros críticos
};
