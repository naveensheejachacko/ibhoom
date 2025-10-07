import React, { useState, useEffect } from 'react';

interface Category {
  id: string;
  name: string;
  parent_id?: string;
}

interface DynamicCategorySelectorProps {
  categories: Category[];
  selectedCategoryId: string;
  onCategorySelect: (categoryId: string) => void;
  error?: string;
}

const DynamicCategorySelector: React.FC<DynamicCategorySelectorProps> = ({
  categories,
  selectedCategoryId,
  onCategorySelect,
  error
}) => {
  const [categoryPath, setCategoryPath] = useState<string[]>([]);

  // Get categories at a specific level driven by current path
  const getCategoriesAtLevel = (level: number) => {
    if (level === 0) return categories.filter(cat => !cat.parent_id);
    const parentId = categoryPath[level - 1];
    if (!parentId) return [];
    return categories.filter(cat => cat.parent_id === parentId);
  };

  // Get category path names for display
  const getCategoryPathNames = () => {
    return categoryPath.map(id => {
      const category = categories.find(cat => cat.id === id);
      return category ? category.name : '';
    });
  };

  // Handle category selection at a specific level
  const handleCategorySelection = (level: number, categoryId: string) => {
    const newPath = categoryPath.slice(0, level);
    if (categoryId) newPath[level] = categoryId; // set selected id at level
    setCategoryPath(newPath);
    if (categoryId) onCategorySelect(categoryId);
  };

  // Build levels dynamically so that after selecting a level with children,
  // the next dropdown appears automatically
  const buildLevels = () => {
    const levels: { level: number; options: Category[] }[] = [] as any;
    let level = 0;
    // Always show level 0
    let options = getCategoriesAtLevel(0);
    if (options.length > 0) levels.push({ level, options });
    // While there is a selection at current level that has children, add next level
    while (categoryPath[level] && categories.some(c => c.parent_id === categoryPath[level])) {
      level += 1;
      options = getCategoriesAtLevel(level);
      if (options.length === 0) break;
      levels.push({ level, options });
    }
    return levels;
  };

  const levels = buildLevels();
  const pathNames = getCategoryPathNames();

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-secondary-700 mb-2">
        Category * (choose deepest applicable)
      </label>
      
      {/* Category Path Display */}
      {pathNames.length > 0 && (
        <div className="text-sm text-secondary-600 mb-2">
          <span className="font-medium">Selected path: </span>
          {pathNames.join(' → ')}
        </div>
      )}

      {/* Dynamic Category Dropdowns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {levels.map(({ level, options }) => (
          <select
            key={level}
            value={categoryPath[level] || ''}
            onChange={(e) => handleCategorySelection(level, e.target.value)}
            className="input-field"
            disabled={level > 0 && !categoryPath[level - 1]}
          >
            <option value="">
              {level === 0 ? 'Select Parent Category' :
               level === 1 ? 'Select Subcategory' :
               `Select Level ${level + 1}`}
            </option>
            {options.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        ))}
      </div>

      {/* Show if there are more levels available */}
      {categoryPath.length > 0 && getCategoriesAtLevel(categoryPath.length).length > 0 && (
        <div className="text-xs text-secondary-500">
          Continue selecting to reach the deepest category level
        </div>
      )}

      {error && (
        <p className="text-xs text-red-600 mt-1">{error}</p>
      )}
    </div>
  );
};

export default DynamicCategorySelector;
