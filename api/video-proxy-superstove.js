// File: /api/video-proxy-superstove.js

export default async function handler(req, res) {
  try {
    const videoUrl = 'https://archive.org/download/SuperStove-English/SuperStove-English.mp4';

    // Fetch the video from the original source
    const videoResponse = await fetch(videoUrl);

    if (!videoResponse.ok) {
      throw new Error(`Failed to fetch video: ${videoResponse.statusText}`);
    }

    // Set the necessary headers
    res.setHeader('Content-Type', 'video/mp4');
    res.setHeader('Cache-Control', 'public, s-maxage=86400, stale-while-revalidate');

    // Manually pipe the stream by iterating over its chunks
    // This is the modern, correct way to handle web streams
    for await (const chunk of videoResponse.body) {
      res.write(chunk);
    }

    res.end(); // End the response after all chunks are sent

  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ error: 'Error fetching video' });
  }
}
