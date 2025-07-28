"use client"

import { useEffect, useState } from 'react';

export default function Page() {
	type BackendMessage = {
		message: string;
	}

	const [data, setData] = useState<BackendMessage | null>(null);

	useEffect(() => {
		fetch('http://localhost:80/api/first-time-seeds')
			.then((res) => res.json())
			.then((data) => setData(data))
			.catch((err) => console.error(err));
	}, []);
	
	return (
		<div>
			<h1>Next.js Frontend</h1>
			<p>Data from FastAPI backend: { data ? data.message : 'Loading...' }</p>
		</div>
	);
}
