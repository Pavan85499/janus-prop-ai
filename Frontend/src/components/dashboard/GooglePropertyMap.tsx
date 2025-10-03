import { useMemo } from 'react';
import { GoogleMap, Marker, InfoWindow, useLoadScript } from '@react-google-maps/api';

type LatLng = { lat: number; lng: number };

export type GMapMarker = {
  id: string;
  position: LatLng;
  label: string;
  subtitle?: string;
  score?: number; // 0-100 for color-coded scoring
};

export default function GooglePropertyMap({
  apiKey,
  center,
  markers,
  height = 360
}: {
  apiKey: string;
  center: LatLng;
  markers: GMapMarker[];
  height?: number;
}) {
  const { isLoaded, loadError } = useLoadScript({ googleMapsApiKey: apiKey });
  const containerStyle = useMemo(() => ({ height: `${height}px`, width: '100%' }), [height]);

  const colorForScore = (s?: number) => {
    if (s === undefined) return 'red';
    if (s >= 85) return '#22c55e'; // green
    if (s >= 70) return '#eab308'; // amber
    return '#ef4444'; // red
  };

  if (loadError) return <div className="text-sm text-destructive">Failed to load Google Maps</div>;
  if (!isLoaded) return <div className="text-sm text-muted-foreground">Loading map...</div>;

  return (
    <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={12} options={{ streetViewControl: false, mapTypeControl: false }}>
      {markers.map(m => (
        <Marker 
          key={m.id}
          position={m.position}
          label={{ text: ' ', color: '#000' }}
          icon={{
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: colorForScore(m.score),
            fillOpacity: 0.9,
            strokeWeight: 1,
            strokeColor: '#111827',
            scale: 8
          }}
        />
      ))}
    </GoogleMap>
  );
}


