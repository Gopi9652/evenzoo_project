export interface CinematicScene {
  key: string;
  type: 'image' | 'video';
  src: string;          // image URL or video URL
  poster?: string;       // fallback/poster image for video (shown while loading, or if video fails)
  sectionId: string;     // the DOM id of the matching content section
  label: string;         // shown in the scene rail tooltip
}