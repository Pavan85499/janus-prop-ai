import { createPortal } from 'react-dom';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, X, Send } from 'lucide-react';
import { useAskJanus } from '@/contexts/AskJanusContext';

export default function AskJanusOverlay() {
	const { isOpen, setIsOpen } = useAskJanus();
	const [mounted, setMounted] = useState(false);
	const [message, setMessage] = useState('');
	const [reply, setReply] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);
	const suggestions = [
		"Find properties with 10%+ cap rates",
		"Show me BRRRR opportunities in Austin",
		"What's the market trend for tax liens?",
		"Analyze my portfolio diversification"
	];

	useEffect(() => setMounted(true), []);
	if (!mounted) return null;
	const root = document.body;

	async function send() {
		if (!message.trim()) return;
		try {
			setLoading(true);
			setReply(null);
			const res = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/ask/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ message })
			});
			if (!res.ok) {
				const text = await res.text();
				throw new Error(text);
			}
			const data = await res.json();
			setReply(data.reply || '');
			setMessage('');
		} catch (e: any) {
			setReply(`Error: ${e?.message || 'Failed to get response'}`);
		} finally {
			setLoading(false);
		}
	}

	return createPortal(
		<div className={`fixed inset-0 z-[1000] ${isOpen ? 'pointer-events-auto' : 'pointer-events-none'}`}>
			{/* Backdrop */}
			<div
				className={`absolute inset-0 bg-black/40 transition-opacity ${isOpen ? 'opacity-100' : 'opacity-0'}`}
				onClick={() => setIsOpen(false)}
			/>
			{/* Panel */}
			<div className={`absolute right-2 sm:right-6 top-16 sm:top-20 w-[95%] sm:w-[520px] transition-all ${isOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
				<Card className="data-card shadow-2xl">
					<CardHeader className="flex flex-row items-center justify-between pb-3">
						<div className="flex items-center gap-3">
							<div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
								<MessageSquare className="w-4 h-4 text-primary-foreground" />
							</div>
							<div>
								<CardTitle className="text-lg font-normal">Ask Janus</CardTitle>
								<div className="flex items-center gap-2">
									<div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
									<span className="text-xs text-muted-foreground">AI Assistant Online</span>
								</div>
							</div>
						</div>
						<Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
							<X className="w-4 h-4" />
						</Button>
					</CardHeader>
					<CardContent className="space-y-4">
						<div className="p-3 bg-primary/10 rounded-lg border border-primary/20">
							<p className="text-sm">
								<span className="font-medium text-primary">Janus AI:</span> {reply ? reply : 'How can I help you analyze the real estate market today?'}
							</p>
						</div>
						<div className="space-y-2">
							<p className="text-xs text-muted-foreground font-medium">Quick Actions:</p>
							<div className="grid grid-cols-1 gap-2">
								{suggestions.map((s, i) => (
									<Badge key={i} variant="outline" className="justify-start text-left p-2 h-auto cursor-pointer hover:bg-primary/10 hover:border-primary/30" onClick={() => setMessage(s)}>
										{s}
									</Badge>
								))}
							</div>
						</div>
						<div className="flex gap-2">
							<Input
								placeholder="Ask about properties, market trends..."
								value={message}
								onChange={(e) => setMessage(e.target.value)}
								className="bg-secondary/20 border-border/50"
								onKeyDown={(e) => {
									if (e.key === 'Enter' && message.trim() && !loading) {
										send();
									}
								}}
							/>
							<Button size="sm" className="bg-gradient-primary glow-primary shrink-0" disabled={!message.trim() || loading} onClick={send}>
								<Send className="w-4 h-4" />
							</Button>
						</div>
						{loading && <p className="text-xs text-muted-foreground">Generating answer...</p>}
					</CardContent>
				</Card>
			</div>
		</div>,
		root
	);
}


