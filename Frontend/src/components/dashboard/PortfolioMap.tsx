import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

type LatLng = { lat: number; lng: number };

export type PortfolioMapMarker = {
  id: string;
  position: LatLng;
  label: string;
  subtitle?: string;
  score?: number; // 0-100 for color-coded markers
};

function Recenter({ center }: { center: LatLng }) {
  const map = useMap();
  useEffect(() => {
    map.setView([center.lat, center.lng], map.getZoom() || 12, { animate: true });
  }, [center.lat, center.lng]);
  return null;
}

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

export default function PortfolioMap({
  center,
  markers,
  height = 360,
  userPosition
}: {
  center: LatLng;
  markers: PortfolioMapMarker[];
  height?: number;
  userPosition?: LatLng | null;
}) {
  return (
    <div style={{ height, width: '100%', borderRadius: 8, overflow: 'hidden' }}>
      <MapContainer center={[center.lat, center.lng]} zoom={12} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        />
        <Recenter center={center} />
        {markers.map(m => {
          const colorForScore = (s?: number) => {
            if (s === undefined) return '#ef4444';
            if (s >= 85) return '#22c55e';
            if (s >= 70) return '#eab308';
            return '#ef4444';
          };
          const icon = L.divIcon({
            className: '',
            html: `<div style="width:14px;height:14px;border-radius:50%;background:${colorForScore(m.score)};border:1px solid #111827;"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7]
          });
          return (
            <Marker key={m.id} position={[m.position.lat, m.position.lng]} icon={icon}>
            <Popup>
              <div style={{ minWidth: 160 }}>
                <div style={{ fontWeight: 600 }}>{m.label}</div>
                {m.subtitle && <div style={{ fontSize: 12, opacity: 0.8 }}>{m.subtitle}</div>}
              </div>
            </Popup>
            </Marker>
          );
        })}
        {userPosition && (
          <Marker position={[userPosition.lat, userPosition.lng]} icon={defaultIcon}>
            <Popup>
              <div style={{ minWidth: 140 }}>
                <div style={{ fontWeight: 600 }}>Your Location</div>
                <div style={{ fontSize: 12, opacity: 0.8 }}>Approximate center</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}


