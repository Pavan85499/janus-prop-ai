import { createContext, useContext, useState, ReactNode } from 'react';

type AskJanusContextType = {
	isOpen: boolean;
	setIsOpen: (open: boolean) => void;
};

const AskJanusContext = createContext<AskJanusContextType | undefined>(undefined);

export function AskJanusProvider({ children }: { children: ReactNode }) {
	const [isOpen, setIsOpen] = useState(false);
	return (
		<AskJanusContext.Provider value={{ isOpen, setIsOpen }}>
			{children}
		</AskJanusContext.Provider>
	);
}

export function useAskJanus() {
	const ctx = useContext(AskJanusContext);
	if (!ctx) throw new Error('useAskJanus must be used within AskJanusProvider');
	return ctx;
}


