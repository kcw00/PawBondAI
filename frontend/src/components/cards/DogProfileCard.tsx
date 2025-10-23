import { useState } from "react";
import { Heart, Info, MapPin, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface DogProfile {
  name: string;
  age: string;
  breed: string;
  photos: string[];
  personalityTags: string[];
  status: "Available" | "Pending" | "Adopted" | "Medical Hold";
  specialNeeds?: string;
  energyLevel: "Low" | "Moderate" | "High";
  size: "Small" | "Medium" | "Large";
  goodWithKids: boolean;
  goodWithPets: boolean;
  hasKoreanProfile?: boolean;
}

interface DogProfileCardProps {
  dog: DogProfile;
  onViewProfile?: () => void;
  onFindMatches?: () => void;
  onTranslate?: () => void;
}

export const DogProfileCard = ({
  dog,
  onViewProfile,
  onFindMatches,
  onTranslate,
}: DogProfileCardProps) => {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  const nextPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev + 1) % dog.photos.length);
  };

  const prevPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev - 1 + dog.photos.length) % dog.photos.length);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Available":
        return "bg-success/20 text-success border-success/30";
      case "Pending":
        return "bg-warning/20 text-warning border-warning/30";
      case "Adopted":
        return "bg-primary/20 text-primary border-primary/30";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  return (
    <Card className="p-5 bg-card border-border hover:shadow-lg transition-all duration-300 animate-fade-in">
      {/* Photo Carousel */}
      <div className="relative mb-4 rounded-lg overflow-hidden bg-muted h-64">
        {dog.photos.length > 0 ? (
          <>
            <img
              src={dog.photos[currentPhotoIndex]}
              alt={`${dog.name} photo ${currentPhotoIndex + 1}`}
              className="w-full h-full object-cover"
            />
            {dog.photos.length > 1 && (
              <>
                <button
                  onClick={prevPhoto}
                  className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-2 hover:bg-black/70 transition-colors"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  onClick={nextPhoto}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white rounded-full p-2 hover:bg-black/70 transition-colors"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex space-x-1">
                  {dog.photos.map((_, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        "h-1.5 w-1.5 rounded-full transition-all",
                        idx === currentPhotoIndex
                          ? "bg-white w-4"
                          : "bg-white/50"
                      )}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Heart className="h-12 w-12 text-muted-foreground" />
          </div>
        )}

        {/* Korean Profile Badge */}
        {dog.hasKoreanProfile && (
          <button
            onClick={onTranslate}
            className="absolute top-2 right-2 bg-warning/90 text-white px-3 py-1 rounded-full text-xs font-semibold hover:bg-warning transition-colors"
          >
            🇰🇷 Translate
          </button>
        )}
      </div>

      {/* Name, Age, Breed */}
      <div className="mb-3">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-xl font-bold text-foreground">{dog.name}</h3>
          <Badge className={cn("border", getStatusColor(dog.status))}>
            {dog.status}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          {dog.age} • {dog.breed}
        </p>
      </div>

      {/* Personality Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        {dog.personalityTags.slice(0, 5).map((tag, idx) => (
          <Badge
            key={idx}
            variant="outline"
            className="bg-primary/10 text-primary border-primary/20"
          >
            {tag}
          </Badge>
        ))}
      </div>

      {/* Special Needs Indicator */}
      {dog.specialNeeds && (
        <div className="mb-4 p-3 bg-warning/10 border border-warning/20 rounded-lg flex items-start">
          <Info className="h-4 w-4 text-warning mr-2 mt-0.5 flex-shrink-0" />
          <div>
            <span className="text-xs font-semibold text-warning block">
              Special Needs:
            </span>
            <span className="text-sm text-foreground">{dog.specialNeeds}</span>
          </div>
        </div>
      )}

      {/* Quick Facts */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-sm">
          <span className="text-muted-foreground">Energy:</span>{" "}
          <span className="font-semibold text-foreground">{dog.energyLevel}</span>
        </div>
        <div className="text-sm">
          <span className="text-muted-foreground">Size:</span>{" "}
          <span className="font-semibold text-foreground">{dog.size}</span>
        </div>
        <div className="text-sm">
          <span className="text-muted-foreground">With Kids:</span>{" "}
          <span className="font-semibold text-foreground">
            {dog.goodWithKids ? "Yes ✓" : "No ✗"}
          </span>
        </div>
        <div className="text-sm">
          <span className="text-muted-foreground">With Pets:</span>{" "}
          <span className="font-semibold text-foreground">
            {dog.goodWithPets ? "Yes ✓" : "No ✗"}
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={onViewProfile}
          className="flex-1 border-border hover:bg-muted"
        >
          View Full Profile
        </Button>
        <Button
          size="sm"
          onClick={onFindMatches}
          className="flex-1 bg-secondary hover:bg-secondary/90 text-secondary-foreground"
        >
          Find Matches
        </Button>
      </div>

      {/* Powered by Badge */}
      <div className="mt-3 pt-3 border-t border-border">
        <span className="text-xs text-muted-foreground">Powered by Elasticsearch</span>
      </div>
    </Card>
  );
};
