// File: /api/video-proxy-superstove.js

export default async function handler(req, res) {
  try {
    const videoUrl = 'https://archive.org/download/SuperStove-English/SuperStove-English.mp4';

    // Fetch the video from the original source
    const videoResponse = await fetch(videoUrl);

    // Check if the request to the video source was successful
    if (!videoResponse.ok) {
      throw new Error(`Failed to fetch video: ${videoResponse.statusText}`);
    }

    // Set the appropriate content type header for the video
    res.setHeader('Content-Type', 'video/mp4');
    
    // Set caching headers to improve performance and reduce function invocations
    // This tells Vercel's Edge Network to cache the content for one day.
    res.setHeader('Cache-Control', 'public, s-maxage=86400, stale-while-revalidate');

    // Pipe the video stream directly to the client's response
    // This is memory-efficient as it doesn't load the whole file.
    await new Promise((resolve, reject) => {
      videoResponse.body.pipe(res);
      videoResponse.body.on('end', resolve);
      videoResponse.body.on('error', reject);
    });

  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ error: 'Error fetching video' });
  }
}
