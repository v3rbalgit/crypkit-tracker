import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Tooltip,
  Paper,
  InputAdornment,
} from '@mui/material';
import DoneIcon from '@mui/icons-material/Done';
import CloseIcon from '@mui/icons-material/Close';
import { motion, AnimatePresence } from 'framer-motion';

interface EditAmountFieldProps {
  initialValue: number;
  onSave: (value: number) => Promise<void>;
  onCancel: () => void;
}

const EditAmountField: React.FC<EditAmountFieldProps> = ({
  initialValue,
  onSave,
  onCancel,
}) => {
  const [value, setValue] = useState(initialValue.toString());
  const [isValid, setIsValid] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
    inputRef.current?.select();
  }, []);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    setValue(newValue);
    setIsValid(newValue !== '' && parseFloat(newValue) > 0);
  };

  const handleSave = async () => {
    if (!isValid) return;
    setIsSaving(true);
    try {
      await onSave(parseFloat(value));
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && isValid) {
      handleSave();
    } else if (event.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Paper elevation={3} sx={{ p: 0.5 }}>
        <TextField
          inputRef={inputRef}
          size="small"
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyPress}
          error={!isValid}
          disabled={isSaving}
          type="number"
          inputProps={{ step: 'any', min: '0' }}
          sx={{ width: '180px' }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Tooltip title="Save (Enter)">
                    <IconButton
                      size="small"
                      onClick={handleSave}
                      disabled={!isValid || isSaving}
                      color="primary"
                    >
                      <DoneIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Cancel (Esc)">
                    <IconButton
                      size="small"
                      onClick={onCancel}
                      disabled={isSaving}
                      color="default"
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </InputAdornment>
            ),
          }}
        />
      </Paper>
    </motion.div>
  );
};

export default EditAmountField;
